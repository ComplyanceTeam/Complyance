"""
Synthetic E-Invoice Dataset Generator

Generates realistic e-invoice data mimicking real-world cross-border B2B trade.
Produces: format_rules.csv, invoices_source.csv, invoices_test.csv, mappings_train.csv
"""

import csv
import json
import random
import re
import os
import sys
import math
from datetime import datetime, timedelta
from collections import Counter

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    FORMAT_RULES, FORMAT_BY_NAME, COUNTRY_FORMAT_MAP, FORMAT_CURRENCIES,
    VAT_PATTERNS, STANDARD_TAX_RATES, COUNTRY_CURRENCIES, TRADE_CORRIDORS,
    PRODUCT_CATALOG, COMPANIES, ERROR_TYPES, ERROR_WEIGHTS,
)

random.seed(42)  # Reproducibility

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


# ═══════════════════════════════════════════════════════════
# VAT NUMBER GENERATORS (country-specific, realistic formats)
# ═══════════════════════════════════════════════════════════

def generate_vat(country: str) -> str:
    """Generate a valid VAT number for the given country."""
    d = lambda n: "".join([str(random.randint(0, 9)) for _ in range(n)])
    generators = {
        "DE": lambda: f"DE{d(9)}",
        "FR": lambda: f"FR{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ0123456789')}{d(9)}",
        "BE": lambda: f"BE0{d(9)}",
        "NL": lambda: f"NL{d(9)}B{d(2)}",
        "MY": lambda: f"MY{d(random.choice([10, 11, 12]))}",
        "SG": lambda: f"SG{d(9)}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}",
        "AT": lambda: f"ATU{d(8)}",
        "IT": lambda: f"IT{d(11)}",
        "FI": lambda: f"FI{d(8)}",
        "NO": lambda: f"NO{d(9)}MVA",
        "SE": lambda: f"SE{d(12)}",
        "CH": lambda: f"CHE{d(9)}",
    }
    gen = generators.get(country)
    return gen() if gen else f"{country}{d(9)}"


def generate_invalid_vat(country: str) -> str:
    """Generate an intentionally invalid VAT number."""
    strategies = [
        lambda: f"{country}{random.randint(100, 999)}",           # Too short
        lambda: f"XX{random.randint(100000, 999999)}",             # Wrong prefix
        lambda: f"{country.lower()}{random.randint(10000, 99999)}",# Lowercase prefix
        lambda: f"{random.randint(1000000, 9999999)}",             # No prefix at all
        lambda: f"{country}{'A' * 5}",                            # Letters instead of digits
    ]
    return random.choice(strategies)()


# ═══════════════════════════════════════════════════════════
# LINE ITEM GENERATORS
# ═══════════════════════════════════════════════════════════

def generate_line_items_flat(num_items: int) -> list:
    """Generate flat line items (simple array, no nesting)."""
    sector = random.choice(list(PRODUCT_CATALOG.keys()))
    products = PRODUCT_CATALOG[sector]
    items = []
    for i in range(num_items):
        product = random.choice(products)
        qty = random.randint(1, 100)
        # Add some price variation (±20%)
        unit_price = round(product[1] * random.uniform(0.8, 1.2), 2)
        line_total = round(qty * unit_price, 2)
        items.append({
            "line_id": i + 1,
            "description": product[0],
            "quantity": qty,
            "unit": product[2],
            "unit_price": unit_price,
            "line_total": line_total,
        })
    return items


def generate_line_items_nested(num_items: int) -> list:
    """Generate nested line items (with sub_items for grouped products)."""
    sector = random.choice(list(PRODUCT_CATALOG.keys()))
    products = PRODUCT_CATALOG[sector]
    items = []
    line_id = 1

    i = 0
    while i < num_items:
        # ~30% chance of a group with sub-items
        if random.random() < 0.3 and (num_items - i) >= 3:
            num_sub = random.randint(2, min(4, num_items - i))
            sub_items = []
            group_total = 0
            for s in range(num_sub):
                product = random.choice(products)
                qty = random.randint(1, 50)
                unit_price = round(product[1] * random.uniform(0.8, 1.2), 2)
                line_total = round(qty * unit_price, 2)
                group_total += line_total
                sub_items.append({
                    "line_id": f"{line_id}.{s+1}",
                    "description": product[0],
                    "quantity": qty,
                    "unit": product[2],
                    "unit_price": unit_price,
                    "line_total": line_total,
                })
            items.append({
                "line_id": line_id,
                "description": f"Assembly Group {line_id}",
                "quantity": 1,
                "unit": "EA",
                "unit_price": round(group_total, 2),
                "line_total": round(group_total, 2),
                "sub_items": sub_items,
            })
            i += num_sub
        else:
            product = random.choice(products)
            qty = random.randint(1, 100)
            unit_price = round(product[1] * random.uniform(0.8, 1.2), 2)
            line_total = round(qty * unit_price, 2)
            items.append({
                "line_id": line_id,
                "description": product[0],
                "quantity": qty,
                "unit": product[2],
                "unit_price": unit_price,
                "line_total": line_total,
            })
            i += 1
        line_id += 1
    return items


def compute_subtotal_from_items(items: list) -> float:
    """Sum line_total from top-level items (not sub_items to avoid double counting)."""
    return round(sum(item["line_total"] for item in items), 2)


# ═══════════════════════════════════════════════════════════
# COMPANY & SELLER/BUYER ID GENERATORS
# ═══════════════════════════════════════════════════════════

def get_seller_for_format(source_format: str) -> tuple:
    """Pick a realistic seller company for the source format's country."""
    fmt = FORMAT_BY_NAME[source_format]
    countries = fmt["used_in_countries"].split(",")
    country = random.choice(countries)
    if country in COMPANIES:
        company = random.choice(COMPANIES[country])
        seller_id = company[0].split()[0].upper()[:4] + f"-{random.randint(1000, 9999)}"
        return seller_id, company[0], country
    seller_id = f"SELL-{random.randint(10000, 99999)}"
    return seller_id, f"Company in {country}", country


def get_buyer_for_country(target_country: str) -> tuple:
    """Pick a realistic buyer company for the target country."""
    if target_country in COMPANIES:
        company = random.choice(COMPANIES[target_country])
        buyer_id = company[0].split()[0].upper()[:4] + f"-{random.randint(1000, 9999)}"
        return buyer_id, company[0]
    buyer_id = f"BUY-{random.randint(10000, 99999)}"
    return buyer_id, f"Buyer in {target_country}"


# ═══════════════════════════════════════════════════════════
# INVOICE GENERATOR
# ═══════════════════════════════════════════════════════════

def pick_trade_corridor() -> tuple:
    """Weighted random selection of a source_format → target_country pair."""
    formats = [tc[0] for tc in TRADE_CORRIDORS]
    countries = [tc[1] for tc in TRADE_CORRIDORS]
    weights = [tc[2] for tc in TRADE_CORRIDORS]
    idx = random.choices(range(len(TRADE_CORRIDORS)), weights=weights, k=1)[0]
    return formats[idx], countries[idx]


def generate_invoice(invoice_id: str, is_credit_note: bool = False,
                     ensure_clean: bool = False) -> dict:
    """
    Generate a single realistic invoice row.

    Args:
        invoice_id: Unique invoice identifier
        is_credit_note: If True, generate negative amounts
        ensure_clean: If True, ensure the invoice has NO natural mapping errors
                      (use target-compatible currency, valid VATs, etc.)
    """
    source_format, target_country = pick_trade_corridor()
    source_rules = FORMAT_BY_NAME[source_format]
    target_format = COUNTRY_FORMAT_MAP.get(target_country, "peppol_bis_3")
    target_rules = FORMAT_BY_NAME.get(target_format, {})

    # Seller from source format's country
    seller_id, seller_name, seller_country = get_seller_for_format(source_format)

    # Buyer from target country
    buyer_id, buyer_name = get_buyer_for_country(target_country)

    # Dates: issue_date in last 2 years, delivery 1-30 days after
    base_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 730))
    issue_date = base_date.strftime("%Y-%m-%d")
    delivery_date = (base_date + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")

    # Currency: for clean invoices, must be supported by target format
    if ensure_clean:
        target_supported = FORMAT_CURRENCIES.get(target_format, ["EUR"])
        seller_currency = COUNTRY_CURRENCIES.get(seller_country, "EUR")
        if seller_currency in target_supported:
            currency = seller_currency
        else:
            currency = target_supported[0]  # Use target's default
    else:
        currency = COUNTRY_CURRENCIES.get(seller_country, "EUR")

    # Tax rate: pick from seller's country standard rates
    tax_rates = STANDARD_TAX_RATES.get(seller_country, [0.19])
    tax_rate = random.choice(tax_rates)

    # Line items
    num_items = random.choices(
        [1, 2, 3, 5, 8, 10, 15, 20, 30, 50],
        weights=[5, 15, 20, 20, 15, 10, 7, 5, 2, 1],
        k=1
    )[0]

    # Line items: for clean invoices, use target-compatible structure
    if ensure_clean:
        # Use the target format's structure to ensure compatibility
        target_structure = target_rules.get("line_item_structure", "flat")
        if target_structure == "nested":
            line_items = generate_line_items_nested(num_items)
        else:
            line_items = generate_line_items_flat(num_items)
    else:
        # Use the source format's line item structure
        if source_rules["line_item_structure"] == "nested":
            line_items = generate_line_items_nested(num_items)
        else:
            line_items = generate_line_items_flat(num_items)

    subtotal = compute_subtotal_from_items(line_items)
    # Clamp subtotal to realistic range
    if subtotal < 50:
        scale = random.uniform(50, 200) / max(subtotal, 0.01)
        for item in line_items:
            item["unit_price"] = round(item["unit_price"] * scale, 2)
            item["line_total"] = round(item["quantity"] * item["unit_price"], 2)
        subtotal = compute_subtotal_from_items(line_items)
    if subtotal > 250000:
        scale = random.uniform(100000, 250000) / subtotal
        for item in line_items:
            item["unit_price"] = round(item["unit_price"] * scale, 2)
            item["line_total"] = round(item["quantity"] * item["unit_price"], 2)
        subtotal = compute_subtotal_from_items(line_items)

    tax_amount = round(subtotal * tax_rate, 2)
    total_amount = round(subtotal + tax_amount, 2)

    # Credit note = negative amounts (only if NOT ensuring clean for non-credit-note-supporting targets)
    if is_credit_note and not ensure_clean:
        subtotal = -abs(subtotal)
        tax_amount = -abs(tax_amount)
        total_amount = -abs(total_amount)

    # VAT numbers
    seller_vat = generate_vat(seller_country)
    buyer_vat = generate_vat(target_country)

    # Payment reference
    payment_reference = f"PAY-{random.randint(100000, 999999)}-{invoice_id.split('-')[-1]}"

    return {
        "invoice_id": invoice_id,
        "source_format": source_format,
        "target_country": target_country,
        "seller_id": seller_id,
        "buyer_id": buyer_id,
        "issue_date": issue_date,
        "currency": currency,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "line_items_json": json.dumps(line_items, ensure_ascii=False),
        "seller_vat": seller_vat,
        "buyer_vat": buyer_vat,
        "payment_reference": payment_reference,
        "delivery_date": delivery_date,
    }


# ═══════════════════════════════════════════════════════════
# ERROR INJECTION & MAPPING GENERATION
# ═══════════════════════════════════════════════════════════

def inject_errors(invoice: dict, target_format_name: str) -> tuple:
    """
    Inject 1-2 realistic errors into an invoice.
    Returns: (modified_invoice, error_list, corrected_fields_dict)
    """
    target_rules = FORMAT_BY_NAME[target_format_name]
    source_rules = FORMAT_BY_NAME[invoice["source_format"]]
    errors = []
    corrections = {}
    inv = dict(invoice)  # Copy

    # Pick 1-2 error types (weighted)
    error_pool = list(ERROR_WEIGHTS.keys())
    error_w = [ERROR_WEIGHTS[e] for e in error_pool]
    num_errors = random.choices([1, 2], weights=[70, 30], k=1)[0]
    chosen_errors = random.choices(error_pool, weights=error_w, k=num_errors)
    chosen_errors = list(set(chosen_errors))  # Deduplicate

    for error_type in chosen_errors:
        if error_type == "tax_amount_mismatch":
            correct_tax = round(abs(inv["subtotal"]) * inv["tax_rate"], 2)
            # Offset by at least 1.00 to always exceed validation tolerance (0.01)
            offset = max(1.00, round(correct_tax * random.uniform(0.02, 0.15), 2))
            inv["tax_amount"] = round(abs(inv["subtotal"]) * inv["tax_rate"] + random.choice([-1, 1]) * offset, 2)
            inv["total_amount"] = round(inv["subtotal"] + inv["tax_amount"], 2)
            errors.append("tax_amount_mismatch")
            corrections["tax_amount"] = str(correct_tax)
            corrections["total_amount"] = str(round(inv["subtotal"] + correct_tax, 2))

        elif error_type == "missing_required_field":
            required = target_rules["required_fields"].split(",")
            # Only blank out fields that can be reasonably missing
            blankable = [f for f in required if f in ("delivery_date", "payment_reference", "buyer_id")]
            if blankable:
                field = random.choice(blankable)
                original_value = inv.get(field, "")
                inv[field] = ""
                errors.append("missing_required_field")
                corrections[field] = str(original_value) if original_value else "REQUIRED"

        elif error_type == "currency_not_supported":
            supported = FORMAT_CURRENCIES.get(target_format_name, ["EUR"])
            # Pick an unsupported currency
            all_currencies = ["EUR", "USD", "GBP", "CHF", "SEK", "NOK", "DKK", "MYR", "SGD", "JPY", "CNY"]
            unsupported = [c for c in all_currencies if c not in supported]
            if unsupported:
                inv["currency"] = random.choice(unsupported)
                errors.append("currency_not_supported")
                corrections["currency"] = supported[0]

        elif error_type == "line_item_structure_incompatible":
            target_structure = target_rules["line_item_structure"]
            # Only inject when target expects flat — add sub_items to make it nested
            # This is the detectable case: nested data → flat-only target
            if target_structure == "flat":
                items = json.loads(inv["line_items_json"])
                if items:
                    items[0]["sub_items"] = [
                        {"line_id": "1.1", "description": "Sub-component",
                         "quantity": 1, "unit": "EA",
                         "unit_price": 10.0, "line_total": 10.0}
                    ]
                    inv["line_items_json"] = json.dumps(items, ensure_ascii=False)
                errors.append("line_item_structure_incompatible")
                corrections["line_item_structure"] = "flat"

        elif error_type == "buyer_vat_missing_for_target":
            target_required = target_rules["required_fields"].split(",")
            if "buyer_vat" in target_required:
                original_buyer_vat = inv["buyer_vat"]
                inv["buyer_vat"] = ""
                errors.append("buyer_vat_missing_for_target")
                corrections["buyer_vat"] = original_buyer_vat

        elif error_type == "seller_vat_format_invalid":
            # Get the seller's country from the source format
            seller_countries = source_rules["used_in_countries"].split(",")
            seller_country = seller_countries[0]
            original_vat = inv["seller_vat"]
            inv["seller_vat"] = generate_invalid_vat(seller_country)
            errors.append("seller_vat_format_invalid")
            corrections["seller_vat"] = original_vat

        elif error_type == "credit_note_not_supported":
            if not target_rules["supports_credit_note"]:
                # Make it a credit note (negative amounts)
                inv["subtotal"] = -abs(inv["subtotal"])
                inv["tax_amount"] = -abs(inv["tax_amount"])
                inv["total_amount"] = -abs(inv["total_amount"])
                errors.append("credit_note_not_supported")
                corrections["subtotal"] = str(abs(inv["subtotal"]))
                corrections["tax_amount"] = str(abs(inv["tax_amount"]))
                corrections["total_amount"] = str(abs(inv["total_amount"]))

    # Deduplicate errors
    errors = list(dict.fromkeys(errors))

    return inv, errors, corrections


def compute_mapping(invoice: dict) -> dict:
    """
    Compute the deterministic mapping result for a clean (no-error) invoice.
    Returns the mapping row for mappings_train.csv.
    """
    target_country = invoice["target_country"]
    target_format = COUNTRY_FORMAT_MAP.get(target_country)

    if not target_format:
        return {
            "invoice_id": invoice["invoice_id"],
            "target_format": "unknown",
            "is_mapping_valid": False,
            "mapping_errors": "missing_required_field",
            "corrected_fields": json.dumps({"target_country": "unsupported"}),
        }

    return {
        "invoice_id": invoice["invoice_id"],
        "target_format": target_format,
        "is_mapping_valid": True,
        "mapping_errors": "",
        "corrected_fields": "{}",
    }


# ═══════════════════════════════════════════════════════════
# CSV WRITERS
# ═══════════════════════════════════════════════════════════

def write_format_rules():
    """Write format_rules.csv."""
    filepath = os.path.join(DATA_DIR, "format_rules.csv")
    fieldnames = [
        "format_id", "format_name", "used_in_countries", "syntax",
        "required_fields", "optional_fields", "tax_id_field_name",
        "line_item_structure", "supports_credit_note", "max_line_items",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rule in FORMAT_RULES:
            row = dict(rule)
            row["supports_credit_note"] = str(row["supports_credit_note"]).lower()
            writer.writerow(row)
    print(f"  ✅ format_rules.csv — {len(FORMAT_RULES)} rows")


def generate_dataset(num_invoices: int, prefix: str, error_rate: float = 0.0):
    """
    Generate invoices and optionally their mappings.

    Args:
        num_invoices: Number of invoices to generate
        prefix: ID prefix ("SRC" for source, "TST" for test)
        error_rate: Fraction of invoices with errors (0.0 to 1.0)

    Returns:
        (invoices_list, mappings_list)
    """
    invoices = []
    mappings = []

    # Determine which invoices get errors
    num_errors = int(num_invoices * error_rate)
    error_indices = set(random.sample(range(num_invoices), num_errors))

    # Track format pair coverage
    format_pairs = Counter()

    for i in range(num_invoices):
        invoice_id = f"INV-{prefix}-{i+1:05d}"

        if i in error_indices:            # Error invoice: start clean, then inject ONLY deliberate errors
            invoice = generate_invoice(invoice_id, is_credit_note=False, ensure_clean=True)

            target_format = COUNTRY_FORMAT_MAP.get(invoice["target_country"], "unknown")
            pair = f"{invoice['source_format']}→{target_format}"
            format_pairs[pair] += 1

            # Inject errors
            modified_invoice, errors, corrections = inject_errors(invoice, target_format)

            if errors:  # Only count if errors were actually injected
                invoices.append(modified_invoice)
                mappings.append({
                    "invoice_id": invoice_id,
                    "target_format": target_format,
                    "is_mapping_valid": False,
                    "mapping_errors": "|".join(errors),
                    "corrected_fields": json.dumps(corrections),
                })
            else:
                # Error injection didn't apply — regenerate as clean
                invoice = generate_invoice(invoice_id, is_credit_note=False, ensure_clean=True)
                target_format = COUNTRY_FORMAT_MAP.get(invoice["target_country"], "unknown")
                pair = f"{invoice['source_format']}→{target_format}"
                format_pairs[pair] += 1
                invoices.append(invoice)
                mappings.append(compute_mapping(invoice))
        else:
            # Clean invoice: ensure no natural mapping errors
            invoice = generate_invoice(invoice_id, is_credit_note=False, ensure_clean=True)

            target_format = COUNTRY_FORMAT_MAP.get(invoice["target_country"], "unknown")
            pair = f"{invoice['source_format']}→{target_format}"
            format_pairs[pair] += 1

            invoices.append(invoice)
            mappings.append(compute_mapping(invoice))

    return invoices, mappings, format_pairs


def write_invoices(invoices: list, filename: str):
    """Write invoices to CSV."""
    filepath = os.path.join(DATA_DIR, filename)
    fieldnames = [
        "invoice_id", "source_format", "target_country", "seller_id", "buyer_id",
        "issue_date", "currency", "subtotal", "tax_rate", "tax_amount",
        "total_amount", "line_items_json", "seller_vat", "buyer_vat",
        "payment_reference", "delivery_date",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(invoices)
    print(f"  ✅ {filename} — {len(invoices)} rows")


def write_mappings(mappings: list, filename: str):
    """Write mappings to CSV."""
    filepath = os.path.join(DATA_DIR, filename)
    fieldnames = [
        "invoice_id", "target_format", "is_mapping_valid",
        "mapping_errors", "corrected_fields",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mappings)
    print(f"  ✅ {filename} — {len(mappings)} rows")


# ═══════════════════════════════════════════════════════════
# DATASET STATISTICS & VALIDATION
# ═══════════════════════════════════════════════════════════

def print_stats(invoices, mappings, format_pairs, label):
    """Print dataset statistics."""
    total = len(invoices)
    errors = sum(1 for m in mappings if not m["is_mapping_valid"])
    error_pct = (errors / total) * 100

    print(f"\n{'='*60}")
    print(f"  📊 {label} Statistics")
    print(f"{'='*60}")
    print(f"  Total invoices:     {total}")
    print(f"  Valid mappings:     {total - errors} ({100 - error_pct:.1f}%)")
    print(f"  Invalid mappings:   {errors} ({error_pct:.1f}%)")

    # Error type breakdown
    error_counts = Counter()
    for m in mappings:
        if m["mapping_errors"]:
            for err in m["mapping_errors"].split("|"):
                error_counts[err] += 1
    if error_counts:
        print(f"\n  Error Type Breakdown:")
        for err, count in error_counts.most_common():
            print(f"    {err}: {count} ({count/errors*100:.1f}%)")

    # Format pair coverage
    print(f"\n  Source→Target Format Pairs ({len(format_pairs)} unique):")
    for pair, count in format_pairs.most_common():
        print(f"    {pair}: {count}")

    # Currency distribution
    currencies = Counter(inv["currency"] for inv in invoices)
    print(f"\n  Currency Distribution:")
    for curr, count in currencies.most_common():
        print(f"    {curr}: {count}")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("\n🔧 E-Invoice Synthetic Dataset Generator")
    print("=" * 60)

    # Step 1: Format rules
    print("\n📁 Step 1: Writing format_rules.csv...")
    write_format_rules()

    # Step 2: Training dataset (3,200 invoices, ~20% errors)
    print("\n📁 Step 2: Generating training dataset...")
    source_invoices, source_mappings, src_pairs = generate_dataset(
        num_invoices=3200,
        prefix="SRC",
        error_rate=0.20,  # 20% error rate
    )
    write_invoices(source_invoices, "invoices_source.csv")
    write_mappings(source_mappings, "mappings_train.csv")
    print_stats(source_invoices, source_mappings, src_pairs, "Training Set")

    # Step 3: Test dataset (850 invoices, ~20% errors)
    print("\n📁 Step 3: Generating test dataset...")
    test_invoices, test_mappings, test_pairs = generate_dataset(
        num_invoices=850,
        prefix="TST",
        error_rate=0.20,
    )
    write_invoices(test_invoices, "invoices_test.csv")
    # Also write test mappings as ground truth (for our own validation)
    write_mappings(test_mappings, "mappings_test_ground_truth.csv")
    print_stats(test_invoices, test_mappings, test_pairs, "Test Set")

    # Final summary
    print(f"\n{'='*60}")
    print("  ✅ All datasets generated successfully!")
    print(f"  📂 Output directory: {DATA_DIR}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
