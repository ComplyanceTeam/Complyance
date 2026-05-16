# E-Invoice Format Transcoder — Team Playbook

> **Hackathon PS-4** | Tech Stack: **Python** | Team Reference Document

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PIPELINE OVERVIEW                            │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │  INPUT ROW   │───▶│  FORMAT      │───▶│  DETERMINISTIC       │   │
│  │  (invoice)   │    │  RESOLVER    │    │  TRANSCODER          │   │
│  └──────────────┘    │              │    │  (field mapping +    │   │
│                      │ source_fmt   │    │   tax rules)         │   │
│                      │ target_fmt   │    └──────────┬───────────┘   │
│                      └──────────────┘               │               │
│                                                     ▼               │
│                                          ┌──────────────────────┐   │
│                                          │  RULE-BASED          │   │
│                                          │  VALIDATOR           │   │
│                                          │  (7 error types)     │   │
│                                          └──────────┬───────────┘   │
│                                                     │               │
│                                                     ▼               │
│                                          ┌──────────────────────┐   │
│                                          │  ML SUPERVISOR       │   │
│                                          │  (error classifier)  │   │
│                                          └──────────┬───────────┘   │
│                                                     │               │
│                                                     ▼               │
│                                          ┌──────────────────────┐   │
│                                          │  OUTPUT ROW          │   │
│                                          │  target_format       │   │
│                                          │  is_mapping_valid    │   │
│                                          │  mapping_errors      │   │
│                                          │  corrected_fields    │   │
│                                          └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Hackathon/
├── flow.md                          # This file (team reference)
├── PS4.txt                          # Problem statement
│
├── data/                            # All generated datasets
│   ├── format_rules.csv             # 8+ format definitions
│   ├── invoices_source.csv          # 3,000+ training invoices
│   ├── mappings_train.csv           # 3,000+ mapping labels
│   ├── invoices_test.csv            # 800+ test invoices
│   └── predictions_output.csv      # Final output predictions
│
├── src/                             # Source code
│   ├── __init__.py
│   ├── config.py                    # Constants, country→format maps, VAT patterns
│   ├── data_generator.py            # Synthetic dataset generation
│   ├── format_resolver.py           # Resolves target_country → target_format
│   ├── transcoder.py                # Deterministic field mapping engine
│   ├── validator.py                 # Rule-based validation (7 error types)
│   ├── feature_engineer.py          # Extract ML features from invoice rows
│   ├── ml_supervisor.py             # Train & predict with classical ML
│   ├── pipeline.py                  # End-to-end orchestrator
│   └── utils.py                     # Helpers (JSON parsing, VAT regex, etc.)
│
├── notebooks/                       # (Optional) EDA & experimentation
│   └── exploration.ipynb
│
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
└── README.md                        # Submission readme
```

---

## 🧩 Module Breakdown

### Module 1: `config.py` — The Brain

This is the **single source of truth** for all deterministic rules.

```python
# COUNTRY → TARGET FORMAT mapping
COUNTRY_FORMAT_MAP = {
    "DE": "xrechnung_ubl",    # or xrechnung_cii
    "FR": "facturx",
    "MY": "pint_my",
    "SG": "pint_sg",
    "BE": "peppol_bis_3",
    "NL": "nlcius",
    "AT": "peppol_bis_3",     # Austria also uses Peppol
    "IT": "peppol_bis_3",     # Italy SDI, simplified to Peppol
}

# SUPPORTED CURRENCIES per format
FORMAT_CURRENCIES = {
    "xrechnung_ubl": ["EUR"],
    "xrechnung_cii": ["EUR"],
    "facturx":       ["EUR"],
    "zugferd":       ["EUR"],
    "peppol_bis_3":  ["EUR", "GBP", "SEK", "DKK", "NOK"],
    "pint_my":       ["MYR", "USD"],
    "pint_sg":       ["SGD", "USD"],
    "nlcius":        ["EUR"],
}

# VAT FORMAT REGEX per country
VAT_PATTERNS = {
    "DE": r"^DE\d{9}$",
    "FR": r"^FR[A-Z0-9]{2}\d{9}$",
    "BE": r"^BE0\d{9}$",
    "NL": r"^NL\d{9}B\d{2}$",
    "MY": r"^MY\d{10,12}$",
    "SG": r"^SG\d{9}[A-Z]$",
    "AT": r"^ATU\d{8}$",
    "IT": r"^IT\d{11}$",
}

# TAX RATES per country (standard rates)
STANDARD_TAX_RATES = {
    "DE": 0.19, "FR": 0.20, "BE": 0.21, "NL": 0.21,
    "MY": 0.06, "SG": 0.09, "AT": 0.20, "IT": 0.22,
}
```

---

### Module 2: `data_generator.py` — Synthetic Dataset Factory

**Generates all 4 CSV files.**

#### Step-by-step logic:

**format_rules.csv (8 rows)**
| format_id | format_name    | used_in_countries | syntax | required_fields                                    | line_item_structure | supports_credit_note | max_line_items |
|-----------|----------------|-------------------|--------|----------------------------------------------------|---------------------|----------------------|----------------|
| 1         | peppol_bis_3   | BE,AT,IT          | UBL    | seller_id,buyer_id,issue_date,currency,subtotal... | nested              | true                 | 999            |
| 2         | xrechnung_ubl  | DE                | UBL    | seller_id,buyer_id,issue_date,currency,subtotal... | nested              | true                 | 500            |
| 3         | xrechnung_cii  | DE                | CII    | seller_id,buyer_id,issue_date,currency,subtotal... | flat                | true                 | 500            |
| 4         | zugferd        | DE,AT             | CII    | seller_id,buyer_id,issue_date,currency,subtotal... | flat                | true                 | 200            |
| 5         | facturx        | FR                | CII    | seller_id,buyer_id,issue_date,currency,subtotal... | flat                | false                | 200            |
| 6         | pint_my        | MY                | UBL    | seller_id,buyer_id,issue_date,currency,subtotal... | flat                | false                | 100            |
| 7         | pint_sg        | SG                | UBL    | seller_id,buyer_id,issue_date,currency,subtotal... | nested              | true                 | 100            |
| 8         | nlcius         | NL                | UBL    | seller_id,buyer_id,issue_date,currency,subtotal... | nested              | true                 | 500            |

**invoices_source.csv (3,000+ rows) & invoices_test.csv (800+ rows)**
- Random `source_format` from format_rules
- Random `target_country` (intentionally different from source country to force transcoding)
- Realistic line_items_json with 1-50 items
- Correct `tax_amount = subtotal × tax_rate` (for valid invoices)
- Deliberately introduce errors in 15-25% of rows

**mappings_train.csv (3,000 rows — 1:1 with invoices_source)**
- For each source invoice, compute the deterministic mapping result
- Mark `is_mapping_valid = true/false`
- Populate `mapping_errors` and `corrected_fields` for invalid ones

#### The 7 Error Types & How to Inject Them:

| Error Type | How to Inject |
|---|---|
| `missing_required_field` | Leave `buyer_id`, `delivery_date`, or `payment_reference` as empty/null |
| `tax_amount_mismatch` | Set `tax_amount ≠ subtotal × tax_rate` (off by random amount) |
| `currency_not_supported` | Use `USD` for a format that only accepts `EUR` |
| `line_item_structure_incompatible` | Source has `nested` items but target requires `flat` (or vice versa) |
| `buyer_vat_missing_for_target` | Leave `buyer_vat` empty when target format requires it |
| `seller_vat_format_invalid` | Use wrong VAT pattern (e.g., `DE123` instead of `DE123456789`) |
| `credit_note_not_supported` | Flag as credit note when target format has `supports_credit_note = false` |

---

### Module 3: `format_resolver.py` — Format Lookup

```python
def resolve_target_format(target_country: str, format_rules: dict) -> str:
    """
    Given a target_country, find the matching format from format_rules.csv
    where used_in_countries contains this country.
    """
    for fmt_id, rule in format_rules.items():
        if target_country in rule["used_in_countries"].split(","):
            return rule["format_name"]
    return None  # Unknown country = error case
```

---

### Module 4: `transcoder.py` — Deterministic Field Mapper

The core engine. Maps fields from source format schema → target format schema.

```
INPUT:  invoice row + source_format_rules + target_format_rules
OUTPUT: mapped field dict ready for validation
```

**Key transformations:**
1. **Syntax conversion**: UBL ↔ CII field name differences
2. **Line item restructuring**: flat ↔ nested
3. **Tax ID field rename**: `seller_vat` → format-specific field name (from `tax_id_field_name`)
4. **Currency preservation**: pass-through (validated later)
5. **Date format normalization**: ensure ISO 8601

**Mapping table concept:**
```python
# Canonical field → UBL field name → CII field name
FIELD_MAP = {
    "seller_id":         {"UBL": "AccountingSupplierParty/PartyID",
                          "CII": "SellerTradeParty/ID"},
    "buyer_id":          {"UBL": "AccountingCustomerParty/PartyID",
                          "CII": "BuyerTradeParty/ID"},
    "issue_date":        {"UBL": "IssueDate",
                          "CII": "IssueDateTime"},
    "subtotal":          {"UBL": "LegalMonetaryTotal/TaxExclusiveAmount",
                          "CII": "SpecifiedTradeSettlementHeaderMonetarySummation/TaxBasisTotalAmount"},
    "tax_amount":        {"UBL": "TaxTotal/TaxAmount",
                          "CII": "SpecifiedTradeSettlementHeaderMonetarySummation/TaxTotalAmount"},
    "total_amount":      {"UBL": "LegalMonetaryTotal/PayableAmount",
                          "CII": "SpecifiedTradeSettlementHeaderMonetarySummation/GrandTotalAmount"},
    # ... etc for all canonical fields
}
```

---

### Module 5: `validator.py` — Rule-Based Error Checker

Runs **all 7 validation checks** on each transcoded invoice.

```python
def validate(invoice: dict, source_rules: dict, target_rules: dict) -> tuple:
    """
    Returns:
        is_valid: bool
        errors: list[str]
        corrections: dict
    """
    errors = []
    corrections = {}

    # 1. Missing required fields
    for field in target_rules["required_fields"].split(","):
        if not invoice.get(field):
            errors.append("missing_required_field")
            corrections[field] = "REQUIRED"

    # 2. Tax amount mismatch
    expected_tax = round(invoice["subtotal"] * invoice["tax_rate"], 2)
    if abs(invoice["tax_amount"] - expected_tax) > 0.01:
        errors.append("tax_amount_mismatch")
        corrections["tax_amount"] = str(expected_tax)

    # 3. Currency not supported
    if invoice["currency"] not in FORMAT_CURRENCIES[target_rules["format_name"]]:
        errors.append("currency_not_supported")
        corrections["currency"] = FORMAT_CURRENCIES[target_rules["format_name"]][0]

    # 4. Line item structure incompatible
    # Check if source structure matches target expectation
    ...

    # 5. Buyer VAT missing
    if not invoice.get("buyer_vat") and "buyer_vat" in target_rules["required_fields"]:
        errors.append("buyer_vat_missing_for_target")

    # 6. Seller VAT format invalid
    # Regex check against target country's VAT pattern
    ...

    # 7. Credit note not supported
    if invoice.get("is_credit_note") and not target_rules["supports_credit_note"]:
        errors.append("credit_note_not_supported")

    is_valid = len(errors) == 0
    return is_valid, errors, corrections
```

---

### Module 6: `feature_engineer.py` — ML Feature Extraction

Extracts numeric/categorical features from each invoice for the ML model.

**Features to extract:**
| Feature | Type | Description |
|---|---|---|
| `source_format_encoded` | categorical | One-hot or label encoded |
| `target_format_encoded` | categorical | One-hot or label encoded |
| `syntax_match` | binary | 1 if source & target use same syntax (UBL/CII) |
| `has_buyer_vat` | binary | 1 if buyer_vat is non-empty |
| `has_seller_vat` | binary | 1 if seller_vat is non-empty |
| `seller_vat_valid` | binary | 1 if passes regex for source country |
| `buyer_vat_valid` | binary | 1 if passes regex for target country |
| `tax_amount_matches` | binary | 1 if tax_amount ≈ subtotal × tax_rate |
| `currency_supported` | binary | 1 if currency in target format's list |
| `num_line_items` | numeric | Count of items in line_items_json |
| `line_structure_match` | binary | 1 if source & target line_item_structure match |
| `subtotal_log` | numeric | log(subtotal) for normalization |
| `supports_credit_note` | binary | Target format's credit note support |
| `missing_field_count` | numeric | Count of required fields that are empty |

---

### Module 7: `ml_supervisor.py` — Classical ML Classifier

**Task 1: Binary classification** → `is_mapping_valid` (true/false)
**Task 2: Multi-label classification** → Which specific errors? (7 labels)

```python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import cross_val_score
import joblib

def train(X_train, y_binary, y_multilabel):
    # Binary: is this mapping valid?
    binary_clf = GradientBoostingClassifier(n_estimators=200)
    binary_clf.fit(X_train, y_binary)

    # Multi-label: which errors?
    multi_clf = MultiOutputClassifier(RandomForestClassifier(n_estimators=150))
    multi_clf.fit(X_train, y_multilabel)

    joblib.dump(binary_clf, "models/binary_clf.pkl")
    joblib.dump(multi_clf, "models/multi_clf.pkl")

def predict(invoice_features):
    binary_clf = joblib.load("models/binary_clf.pkl")
    multi_clf = joblib.load("models/multi_clf.pkl")

    is_valid = binary_clf.predict([invoice_features])[0]
    error_flags = multi_clf.predict([invoice_features])[0]
    return is_valid, error_flags
```

---

### Module 8: `pipeline.py` — End-to-End Orchestrator

```python
def process_invoice(invoice_row: dict, format_rules: dict, ml_models: dict) -> dict:
    """
    Full pipeline for one invoice row.

    Returns dict with: target_format, is_mapping_valid, mapping_errors, corrected_fields
    """
    # Step 1: Resolve target format
    target_format = resolve_target_format(invoice_row["target_country"], format_rules)

    # Step 2: Deterministic transcoding
    transcoded = transcode(invoice_row, source_rules, target_rules)

    # Step 3: Rule-based validation
    is_valid_rules, errors_rules, corrections = validate(transcoded, source_rules, target_rules)

    # Step 4: ML supervisor (second opinion)
    features = extract_features(invoice_row, source_rules, target_rules)
    is_valid_ml, error_flags_ml = ml_predict(features)

    # Step 5: Combine (rules take priority, ML catches edge cases)
    final_errors = merge_errors(errors_rules, error_flags_ml)
    is_valid = is_valid_rules and is_valid_ml

    return {
        "invoice_id": invoice_row["invoice_id"],
        "target_format": target_format,
        "is_mapping_valid": is_valid,
        "mapping_errors": "|".join(final_errors) if final_errors else "",
        "corrected_fields": json.dumps(corrections) if corrections else "{}"
    }
```

## 🔑 Critical Success Factors

### 1. Generalization (MOST IMPORTANT)
> The hidden test dataset will have the **same schema but different data**.
> Your rules and ML model must not overfit to your synthetic data.

**How to ensure this:**
- Rules in `config.py` should be based on **real-world e-invoicing standards**, not hardcoded to your synthetic data
- ML model should use **format-aware features** (syntax match, currency support, VAT validity), not invoice-specific features (specific seller IDs, specific amounts)
- Test with varied distributions

### 2. Deterministic First, ML Second
- The rule-based validator should catch **~90%+ of errors** on its own
- ML supervisor is a **safety net** for edge cases and ambiguous mappings
- Judges want to see **mapping tables and validation logic**, not a black box

### 3. The 6 Required Format Pairs
Ensure you cover at least 6 distinct source→target combinations:
1. `xrechnung_ubl` (DE) → `facturx` (FR) — UBL to CII syntax switch
2. `facturx` (FR) → `peppol_bis_3` (BE) — CII to UBL syntax switch
3. `pint_my` (MY) → `xrechnung_ubl` (DE) — cross-region
4. `peppol_bis_3` (BE) → `pint_sg` (SG) — UBL to UBL, different rules
5. `nlcius` (NL) → `zugferd` (DE) — UBL to CII
6. `xrechnung_cii` (DE) → `pint_my` (MY) — CII to UBL

### 4. Error Distribution in Dataset
Target: **15-25% error rate** across the 7 types.
Suggested distribution (of the error rows):
- `tax_amount_mismatch`: 25%
- `missing_required_field`: 20%
- `seller_vat_format_invalid`: 15%
- `buyer_vat_missing_for_target`: 15%
- `currency_not_supported`: 10%
- `line_item_structure_incompatible`: 10%
- `credit_note_not_supported`: 5%

---

## 📦 Dependencies (`requirements.txt`)

```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
xgboost>=2.0
faker>=18.0
joblib>=1.3
```

---

## ✅ Acceptance Checklist

- [ ] `format_rules.csv` has ≥ 8 rows with correct schemas
- [ ] `invoices_source.csv` has ≥ 3,000 rows
- [ ] `mappings_train.csv` has ≥ 3,000 rows (1:1 with source)
- [ ] `invoices_test.csv` has ≥ 800 rows
- [ ] ≥ 6 distinct source→target format pairs covered
- [ ] 15-25% of invoices have mapping errors
- [ ] All 7 error types are represented
- [ ] Pipeline processes single row → outputs correct schema
- [ ] Pipeline processes entire test CSV → outputs predictions CSV
- [ ] ML model trained and integrated
- [ ] Code is clean, modular, documented
- [ ] README.md explains approach clearly
