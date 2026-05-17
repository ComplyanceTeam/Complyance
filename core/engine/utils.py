"""
Utility functions for E-Invoice Format Transcoder.
VAT validation, JSON helpers, line item structure operations.
"""

import re
import json
from config import VAT_PATTERNS, FORMAT_CURRENCIES, COUNTRY_FORMAT_MAP


# ═══════════════════════════════════════════════════════════
# VAT NUMBER VALIDATION
# ═══════════════════════════════════════════════════════════

def validate_vat_format(vat_number: str, country: str) -> bool:
    """
    Validate a VAT number against the country's known regex pattern.
    Returns True if valid, False if invalid or country unknown.
    """
    if not vat_number or not vat_number.strip():
        return False

    pattern = VAT_PATTERNS.get(country)
    if not pattern:
        # Unknown country — can't validate, assume valid
        return True

    return bool(re.match(pattern, vat_number.strip()))


def infer_country_from_vat(vat_number: str) -> str:
    """
    Infer the country code from a VAT number prefix.
    Returns 2-letter country code or None.
    """
    if not vat_number or len(vat_number) < 2:
        return None

    # Special cases: 3-letter prefixes
    if vat_number.startswith("ATU"):
        return "AT"
    if vat_number.startswith("CHE"):
        return "CH"

    # Standard: 2-letter prefix
    prefix = vat_number[:2].upper()
    if prefix in VAT_PATTERNS:
        return prefix

    return None


# ═══════════════════════════════════════════════════════════
# CURRENCY VALIDATION
# ═══════════════════════════════════════════════════════════

def is_currency_supported(currency: str, target_format: str) -> bool:
    """Check if a currency is supported by the target format."""
    supported = FORMAT_CURRENCIES.get(target_format, [])
    return currency in supported


def get_default_currency(target_format: str) -> str:
    """Get the first (default/primary) supported currency for a format."""
    supported = FORMAT_CURRENCIES.get(target_format, ["EUR"])
    return supported[0] if supported else "EUR"


# ═══════════════════════════════════════════════════════════
# TAX CALCULATION VALIDATION
# ═══════════════════════════════════════════════════════════

def validate_tax_calculation(subtotal: float, tax_rate: float, tax_amount: float,
                              tolerance: float = 0.01) -> tuple:
    """
    Validate that tax_amount ≈ subtotal × tax_rate.

    Returns:
        (is_valid: bool, expected_tax: float)
    """
    expected_tax = round(abs(subtotal) * tax_rate, 2)
    actual_tax = abs(tax_amount)
    is_valid = abs(actual_tax - expected_tax) <= tolerance
    return is_valid, expected_tax


def validate_total(subtotal: float, tax_amount: float, total_amount: float,
                   tolerance: float = 0.01) -> tuple:
    """
    Validate that total_amount ≈ subtotal + tax_amount.

    Returns:
        (is_valid: bool, expected_total: float)
    """
    expected_total = round(subtotal + tax_amount, 2)
    is_valid = abs(total_amount - expected_total) <= tolerance
    return is_valid, expected_total


# ═══════════════════════════════════════════════════════════
# LINE ITEM STRUCTURE OPERATIONS
# ═══════════════════════════════════════════════════════════

def parse_line_items(line_items_json: str) -> list:
    """Safely parse line_items_json string to list."""
    if not line_items_json:
        return []
    try:
        items = json.loads(line_items_json)
        return items if isinstance(items, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def detect_line_item_structure(items: list) -> str:
    """
    Detect whether line items are flat or nested.
    Returns 'nested' if any item has sub_items, 'flat' otherwise.
    """
    if not items:
        return "flat"
    for item in items:
        if "sub_items" in item and item["sub_items"]:
            return "nested"
    return "flat"


def flatten_line_items(items: list) -> list:
    """
    Flatten nested line items into a flat list.
    Sub-items are promoted to top level with adjusted line_ids.
    """
    flat_items = []
    line_counter = 1

    for item in items:
        sub_items = item.pop("sub_items", None)
        item_copy = dict(item)
        item_copy["line_id"] = line_counter
        flat_items.append(item_copy)
        line_counter += 1

        if sub_items:
            for sub in sub_items:
                sub_copy = dict(sub)
                sub_copy["line_id"] = line_counter
                flat_items.append(sub_copy)
                line_counter += 1

    return flat_items


def nest_line_items(items: list, group_size: int = 3) -> list:
    """
    Group flat line items into nested structure.
    Every `group_size` items are wrapped under a parent group.
    """
    if len(items) <= 1:
        return items

    nested = []
    line_counter = 1

    for i in range(0, len(items), group_size):
        group = items[i:i + group_size]
        if len(group) > 1:
            group_total = sum(item.get("line_total", 0) for item in group)
            nested.append({
                "line_id": line_counter,
                "description": f"Item Group {line_counter}",
                "quantity": 1,
                "unit": "EA",
                "unit_price": round(group_total, 2),
                "line_total": round(group_total, 2),
                "sub_items": group,
            })
        else:
            item = dict(group[0])
            item["line_id"] = line_counter
            nested.append(item)
        line_counter += 1

    return nested


# ═══════════════════════════════════════════════════════════
# FIELD PRESENCE CHECKS
# ═══════════════════════════════════════════════════════════

def is_field_empty(value) -> bool:
    """Check if a field value is empty/missing."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, float) and value != value:  # NaN check
        return True
    return False


def clean_nan_values(data):
    """
    Recursively convert NaN values to None in dictionaries and lists.
    Useful for JSON serialization where NaN is not allowed.
    """
    import pandas as pd
    if isinstance(data, dict):
        return {
            key: clean_nan_values(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [
            clean_nan_values(item)
            for item in data
        ]
    elif isinstance(data, float) and (data != data): # Standard NaN check
        return None
    elif pd.isna(data) if 'pd' in globals() else False:
        return None
    else:
        return data


def get_missing_required_fields(invoice: dict, required_fields: list) -> list:
    """
    Check which required fields are missing/empty in an invoice.
    Returns list of missing field names.
    """
    missing = []
    for field in required_fields:
        field = field.strip()
        if field not in invoice or is_field_empty(invoice.get(field)):
            missing.append(field)
    return missing


# ═══════════════════════════════════════════════════════════
# CREDIT NOTE DETECTION
# ═══════════════════════════════════════════════════════════

def is_credit_note(invoice: dict) -> bool:
    """
    Detect if an invoice is a credit note.
    Credit notes are identified by negative subtotal/total amounts.
    """
    subtotal = float(invoice.get("subtotal", 0))
    total = float(invoice.get("total_amount", 0))
    return subtotal < 0 or total < 0
