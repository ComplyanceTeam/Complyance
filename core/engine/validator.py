"""
Validator — Rule-based validation engine for e-invoice mappings.

Checks all 7 mapping error types defined in the problem statement:
1. missing_required_field
2. tax_amount_mismatch
3. currency_not_supported
4. line_item_structure_incompatible
5. buyer_vat_missing_for_target
6. seller_vat_format_invalid
7. credit_note_not_supported
"""

import json
from utils import (
    validate_vat_format, infer_country_from_vat,
    is_currency_supported, get_default_currency,
    validate_tax_calculation, validate_total,
    parse_line_items, detect_line_item_structure,
    is_field_empty, get_missing_required_fields,
    is_credit_note,
)
from config import FORMAT_CURRENCIES


# ═══════════════════════════════════════════════════════════
# VALIDATION ENGINE
# ═══════════════════════════════════════════════════════════

class Validator:
    """
    Rule-based validator that checks an invoice against target
    format requirements and detects all 7 mapping error types.
    """

    def __init__(self, source_rules: dict, target_rules: dict):
        self.source_rules = source_rules
        self.target_rules = target_rules
        self.target_format = target_rules["format_name"]
        self.target_required = [
            f.strip() for f in target_rules["required_fields"].split(",")
        ]

    def validate(self, invoice: dict) -> tuple:
        """
        Run all 7 validation checks on an invoice.

        Args:
            invoice: Dict with canonical invoice fields

        Returns:
            (is_valid: bool, errors: list[str], corrections: dict)
        """
        errors = []
        corrections = {}

        # Run each check
        self._check_missing_required_fields(invoice, errors, corrections)
        self._check_tax_amount_mismatch(invoice, errors, corrections)
        self._check_currency_not_supported(invoice, errors, corrections)
        self._check_line_item_structure(invoice, errors, corrections)
        self._check_buyer_vat_missing(invoice, errors, corrections)
        self._check_seller_vat_format(invoice, errors, corrections)
        self._check_credit_note_support(invoice, errors, corrections)
        self._check_max_line_items(invoice, errors, corrections)

        # Deduplicate errors while preserving order
        seen = set()
        unique_errors = []
        for e in errors:
            if e not in seen:
                seen.add(e)
                unique_errors.append(e)

        is_valid = len(unique_errors) == 0
        return is_valid, unique_errors, corrections

    # ─────────────────────────────────────────────────────
    # CHECK 8: Max Line Items Exceeded
    # ─────────────────────────────────────────────────────
    def _check_max_line_items(self, invoice: dict, errors: list, corrections: dict):
        """
        Check if the number of line items exceeds the target format's limit.
        """
        max_items = self.target_rules.get("max_line_items", 999)
        items = parse_line_items(invoice.get("line_items_json", "[]"))
        if len(items) > max_items:
            errors.append("max_line_items_exceeded")
            corrections["line_items_json"] = f"TOTAL_ITEMS_{len(items)}_EXCEEDS_LIMIT_{max_items}"

    # ─────────────────────────────────────────────────────
    # CHECK 1: Missing Required Fields
    # ─────────────────────────────────────────────────────
    def _check_missing_required_fields(self, invoice: dict, errors: list, corrections: dict):
        """
        Check if any fields required by the target format are missing/empty.
        Excludes buyer_vat (handled separately) and line_items_json.
        """
        # Fields to check for emptiness (not buyer_vat, handled in check 5)
        check_fields = [f for f in self.target_required
                        if f not in ("buyer_vat", "line_items_json", "invoice_id",
                                     "subtotal", "tax_rate", "tax_amount", "total_amount")]

        for field in check_fields:
            value = invoice.get(field, "")
            if is_field_empty(value):
                errors.append("missing_required_field")
                corrections[field] = "REQUIRED"

    # ─────────────────────────────────────────────────────
    # CHECK 2: Tax Amount Mismatch
    # ─────────────────────────────────────────────────────
    def _check_tax_amount_mismatch(self, invoice: dict, errors: list, corrections: dict):
        """
        Verify that tax_amount ≈ subtotal × tax_rate (within tolerance).
        """
        try:
            subtotal = float(invoice.get("subtotal", 0))
            tax_rate = float(invoice.get("tax_rate", 0))
            tax_amount = float(invoice.get("tax_amount", 0))
            total_amount = float(invoice.get("total_amount", 0))
        except (ValueError, TypeError):
            errors.append("tax_amount_mismatch")
            corrections["tax_amount"] = "INVALID_NUMBER"
            return

        # Check tax calculation
        tax_valid, expected_tax = validate_tax_calculation(subtotal, tax_rate, tax_amount)
        if not tax_valid:
            errors.append("tax_amount_mismatch")
            # Correct based on sign (credit notes have negative)
            if subtotal < 0:
                corrections["tax_amount"] = str(-expected_tax)
                corrections["total_amount"] = str(round(subtotal + (-expected_tax), 2))
            else:
                corrections["tax_amount"] = str(expected_tax)
                corrections["total_amount"] = str(round(subtotal + expected_tax, 2))

    # ─────────────────────────────────────────────────────
    # CHECK 3: Currency Not Supported
    # ─────────────────────────────────────────────────────
    def _check_currency_not_supported(self, invoice: dict, errors: list, corrections: dict):
        """
        Check if the invoice currency is supported by the target format.
        """
        currency = invoice.get("currency", "")
        if currency and not is_currency_supported(currency, self.target_format):
            errors.append("currency_not_supported")
            corrections["currency"] = get_default_currency(self.target_format)

    # ─────────────────────────────────────────────────────
    # CHECK 4: Line Item Structure Incompatible
    # ─────────────────────────────────────────────────────
    def _check_line_item_structure(self, invoice: dict, errors: list, corrections: dict):
        """
        Check if the invoice's line item structure is compatible
        with the target format's expected structure.

        Incompatibility: invoice data contains nested items (sub_items)
        but target format only supports flat structure.
        """
        items = parse_line_items(invoice.get("line_items_json", "[]"))
        actual_structure = detect_line_item_structure(items)
        target_structure = self.target_rules["line_item_structure"]

        # Any invoice with nested data going to a flat-only target = incompatible
        if actual_structure == "nested" and target_structure == "flat":
            errors.append("line_item_structure_incompatible")
            corrections["line_item_structure"] = "flat"

    # ─────────────────────────────────────────────────────
    # CHECK 5: Buyer VAT Missing for Target
    # ─────────────────────────────────────────────────────
    def _check_buyer_vat_missing(self, invoice: dict, errors: list, corrections: dict):
        """
        Check if buyer_vat is required by target format but missing.
        """
        if "buyer_vat" in self.target_required:
            buyer_vat = invoice.get("buyer_vat", "")
            if is_field_empty(buyer_vat):
                errors.append("buyer_vat_missing_for_target")
                corrections["buyer_vat"] = "REQUIRED"

    # ─────────────────────────────────────────────────────
    # CHECK 6: Seller VAT Format Invalid
    # ─────────────────────────────────────────────────────
    def _check_seller_vat_format(self, invoice: dict, errors: list, corrections: dict):
        """
        Check if the seller's VAT number matches the expected format
        for the seller's country (inferred from VAT prefix).
        """
        seller_vat = invoice.get("seller_vat", "")
        if is_field_empty(seller_vat):
            return  # Missing VAT handled by check 1 if required

        # Infer seller country from source format
        source_countries = self.source_rules["used_in_countries"].split(",")
        seller_country = infer_country_from_vat(seller_vat)

        # If we can infer the country, validate the format
        if seller_country:
            if not validate_vat_format(seller_vat, seller_country):
                errors.append("seller_vat_format_invalid")
                corrections["seller_vat"] = f"INVALID_FORMAT_FOR_{seller_country}"
        else:
            # Can't infer country from prefix — check against all source countries
            valid_for_any = False
            for country in source_countries:
                country = country.strip()
                if validate_vat_format(seller_vat, country):
                    valid_for_any = True
                    break
            if not valid_for_any and seller_vat:
                errors.append("seller_vat_format_invalid")
                corrections["seller_vat"] = f"INVALID_FORMAT_FOR_{source_countries[0].strip()}"

    # ─────────────────────────────────────────────────────
    # CHECK 7: Credit Note Not Supported
    # ─────────────────────────────────────────────────────
    def _check_credit_note_support(self, invoice: dict, errors: list, corrections: dict):
        """
        Check if the invoice is a credit note (negative amounts)
        and the target format doesn't support credit notes.
        """
        if is_credit_note(invoice) and not self.target_rules["supports_credit_note"]:
            errors.append("credit_note_not_supported")
            subtotal = float(invoice.get("subtotal", 0))
            tax_amount = float(invoice.get("tax_amount", 0))
            total_amount = float(invoice.get("total_amount", 0))
            corrections["subtotal"] = str(abs(subtotal))
            corrections["tax_amount"] = str(abs(tax_amount))
            corrections["total_amount"] = str(abs(total_amount))
