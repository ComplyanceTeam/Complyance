"""
Transcoder — Deterministic field mapping engine.

Maps invoice fields from source format schema to target format schema.
Handles UBL ↔ CII syntax differences, line item restructuring,
and tax ID field renaming.
"""

import json
from .utils import (
    parse_line_items, detect_line_item_structure,
    flatten_line_items, nest_line_items,
)


# ═══════════════════════════════════════════════════════════
# UBL ↔ CII FIELD MAPPING TABLES
# Based on real Peppol BIS 3.0, XRechnung, Factur-X standards
# ═══════════════════════════════════════════════════════════

# Canonical field → UBL XML path
UBL_FIELD_MAP = {
    "invoice_id":        "Invoice/ID",
    "seller_id":         "AccountingSupplierParty/Party/PartyIdentification/ID",
    "buyer_id":          "AccountingCustomerParty/Party/PartyIdentification/ID",
    "issue_date":        "Invoice/IssueDate",
    "currency":          "Invoice/DocumentCurrencyCode",
    "subtotal":          "LegalMonetaryTotal/TaxExclusiveAmount",
    "tax_rate":          "TaxTotal/TaxSubtotal/Percent",
    "tax_amount":        "TaxTotal/TaxAmount",
    "total_amount":      "LegalMonetaryTotal/PayableAmount",
    "seller_vat":        "AccountingSupplierParty/PartyTaxScheme/CompanyID",
    "buyer_vat":         "AccountingCustomerParty/PartyTaxScheme/CompanyID",
    "payment_reference": "PaymentMeans/PaymentID",
    "delivery_date":     "Delivery/ActualDeliveryDate",
    "line_items_json":   "InvoiceLine",
}

# Canonical field → CII XML path
CII_FIELD_MAP = {
    "invoice_id":        "ExchangedDocument/ID",
    "seller_id":         "SellerTradeParty/ID",
    "buyer_id":          "BuyerTradeParty/ID",
    "issue_date":        "ExchangedDocument/IssueDateTime",
    "currency":          "InvoiceCurrencyCode",
    "subtotal":          "SpecifiedTradeSettlementHeaderMonetarySummation/TaxBasisTotalAmount",
    "tax_rate":          "ApplicableTradeTax/RateApplicablePercent",
    "tax_amount":        "SpecifiedTradeSettlementHeaderMonetarySummation/TaxTotalAmount",
    "total_amount":      "SpecifiedTradeSettlementHeaderMonetarySummation/GrandTotalAmount",
    "seller_vat":        "SellerTradeParty/SpecifiedTaxRegistration/ID",
    "buyer_vat":         "BuyerTradeParty/SpecifiedTaxRegistration/ID",
    "payment_reference": "SpecifiedTradePaymentTerms/DirectDebitMandateID",
    "delivery_date":     "ActualDeliverySupplyChainEvent/OccurrenceDateTime",
    "line_items_json":   "IncludedSupplyChainTradeLineItem",
}

# Syntax to field map
SYNTAX_FIELD_MAPS = {
    "UBL": UBL_FIELD_MAP,
    "CII": CII_FIELD_MAP,
}


# ═══════════════════════════════════════════════════════════
# TRANSCODER ENGINE
# ═══════════════════════════════════════════════════════════

class Transcoder:
    """
    Deterministic transcoder that maps invoice fields from
    source format to target format.
    """

    def __init__(self, source_rules: dict, target_rules: dict):
        """
        Args:
            source_rules: Format rules dict for source format
            target_rules: Format rules dict for target format
        """
        self.source_rules = source_rules
        self.target_rules = target_rules
        self.source_syntax = source_rules["syntax"]
        self.target_syntax = target_rules["syntax"]
        self.source_field_map = SYNTAX_FIELD_MAPS.get(self.source_syntax, UBL_FIELD_MAP)
        self.target_field_map = SYNTAX_FIELD_MAPS.get(self.target_syntax, UBL_FIELD_MAP)

    def transcode(self, invoice: dict) -> dict:
        """
        Transcode an invoice from source format to target format.

        This performs:
        1. Field mapping (canonical fields remain, XML paths are metadata)
        2. Line item structure conversion (flat ↔ nested)
        3. Tax ID field name adaptation
        4. Field value pass-through for canonical fields

        Args:
            invoice: Dict with canonical field names

        Returns:
            Transcoded invoice dict with target format metadata
        """
        transcoded = {}

        # Step 1: Copy all canonical fields (they stay the same)
        canonical_fields = [
            "invoice_id", "seller_id", "buyer_id", "issue_date",
            "currency", "subtotal", "tax_rate", "tax_amount",
            "total_amount", "seller_vat", "buyer_vat",
            "payment_reference", "delivery_date",
        ]
        for field in canonical_fields:
            transcoded[field] = invoice.get(field, "")

        # Step 2: Handle line item structure conversion
        transcoded["line_items_json"] = self._transcode_line_items(
            invoice.get("line_items_json", "[]")
        )

        # Step 3: Add target format metadata
        transcoded["_target_format"] = self.target_rules["format_name"]
        transcoded["_target_syntax"] = self.target_syntax
        transcoded["_source_format"] = self.source_rules["format_name"]
        transcoded["_source_syntax"] = self.source_syntax
        transcoded["_syntax_changed"] = self.source_syntax != self.target_syntax

        # Step 4: Record field mapping paths for traceability
        transcoded["_field_mappings"] = {
            field: {
                "source_path": self.source_field_map.get(field, field),
                "target_path": self.target_field_map.get(field, field),
            }
            for field in canonical_fields
        }

        return transcoded

    def _transcode_line_items(self, line_items_json: str) -> str:
        """
        Convert line items between flat and nested structures
        based on source and target format requirements.
        """
        items = parse_line_items(line_items_json)
        if not items:
            return "[]"

        source_structure = self.source_rules["line_item_structure"]
        target_structure = self.target_rules["line_item_structure"]
        actual_structure = detect_line_item_structure(items)

        # If structures match, pass through
        if actual_structure == target_structure:
            return json.dumps(items, ensure_ascii=False)

        # Nested → Flat: flatten sub_items to top level
        if actual_structure == "nested" and target_structure == "flat":
            flattened = flatten_line_items(items)
            return json.dumps(flattened, ensure_ascii=False)

        # Flat → Nested: group items
        if actual_structure == "flat" and target_structure == "nested":
            nested = nest_line_items(items)
            return json.dumps(nested, ensure_ascii=False)

        return json.dumps(items, ensure_ascii=False)

    def get_required_fields(self) -> list:
        """Get list of required fields for the target format."""
        return [f.strip() for f in self.target_rules["required_fields"].split(",")]

    def get_optional_fields(self) -> list:
        """Get list of optional fields for the target format."""
        optional = self.target_rules.get("optional_fields", "")
        return [f.strip() for f in optional.split(",") if f.strip()]

    def is_syntax_change(self) -> bool:
        """Check if transcoding involves a syntax change (UBL↔CII)."""
        return self.source_syntax != self.target_syntax

    def get_max_line_items(self) -> int:
        """Get max allowed line items for target format."""
        return self.target_rules.get("max_line_items", 999)
