# Intelligent E-Invoice Transcoder and Validation Engine

## Project Overview

This project is an intelligent backend pipeline developed for PS-4: E-Invoice Format Transcoder.

The system accepts invoices in multiple formats such as:

- CSV
- JSON
- XML

The pipeline:

1. Parses the invoice
2. Converts it into a standard format
3. Performs preprocessing and feature engineering
4. Uses Machine Learning to detect invoice mapping errors
5. Applies deterministic correction logic
6. Dynamically transcodes the invoice into the required target format
7. Generates final mapped invoice outputs

The project combines:

- Machine Learning
- Deterministic Business Rules
- Dynamic Format Mapping
- Intelligent Invoice Validation
- Multi-format Invoice Transcoding

---

# Complete Pipeline Flow

```text
User Input Invoice
        ↓
File Type Detection
        ↓
XML / JSON / CSV Parsing
        ↓
Canonical Invoice Conversion
        ↓
Preprocessing & Feature Engineering
        ↓
Machine Learning Prediction
        ↓
Error Detection
        ↓
Deterministic Correction Engine
        ↓
Dynamic Rule-Based Mapper
        ↓
Final Target Invoice Output
```

---

# Project Structure

```text
backend_process/
│
├── data/
│   ├── format_rules.csv
│   ├── invoices_source.csv
│   ├── invoices_test.csv
│
├── models/
│   ├── xgboost_multioutput_model.pkl
│   ├── label_encoders.pkl
│   ├── feature_columns.pkl
│   └── target_columns.pkl
│
├── parsers/
│   ├── xml_to_csv.py
│   ├── json_to_csv.py
│   └── csv_loader.py
│
├── pipeline/
│   ├── preprocess.py
│   ├── predict.py
│   ├── correction.py
│   └── mapper.py
│
├── converted/
├── processed/
├── outputs/
│
├── start.py
│
└── requirements.txt
```

---

# Main Execution File

# start.py

This is the main controller of the project.

Responsibilities:

- Accept user invoice input
- Detect input type
- Route invoice to parser
- Run preprocessing
- Run ML prediction
- Run correction engine
- Run transcoder mapper
- Generate outputs

---

# Runtime Flow

```text
python start.py
```

The console asks:

```text
Enter invoice file path:
```

Example:

```text
data/invoices_test.csv
```

---

# File Parsing Layer

The parser layer converts different input formats into a standard CSV structure.

---

# xml\_to\_csv.py

Purpose:

Convert XML invoice files into CSV.

Flow:

```text
XML File
    ↓
xmltodict Parsing
    ↓
Flatten Structure
    ↓
CSV Output
```

Output:

```text
converted/<filename>.csv
```

---

# json\_to\_csv.py

Purpose:

Convert JSON invoices into CSV.

Flow:

```text
JSON
    ↓
json.load()
    ↓
pd.json_normalize()
    ↓
CSV
```

Output:

```text
converted/<filename>.csv
```

---

# csv\_loader.py

Purpose:

Load already existing CSV invoice files.

No transformation occurs.

---

# Canonical Invoice Concept

Invoices from different countries and formats use different field names.

Example:

| Source Field   | Canonical Field |
| -------------- | --------------- |
| mwst\_nummer   | seller\_vat     |
| montant\_ht    | subtotal        |
| invoice\_total | total\_amount   |

The project internally converts everything into a canonical schema.

This allows:

- common ML features
- common validation logic
- unified transcoding

---

# Preprocessing Layer

# preprocess.py

Purpose:

Convert invoice data into model-ready features.

Responsibilities:

- merge invoice + format rules
- create target format
- perform feature engineering
- extract JSON insights
- encode categorical data
- align features with training schema

---

# format\_rules.csv Usage

The system dynamically reads invoice rules from:

```text
format_rules.csv
```

This file controls:

- required fields
- optional fields
- supported currencies
- syntax type
- line item structure
- VAT field names
- credit note support

The transcoder is completely rule-driven.

---

# Feature Engineering

The preprocessing layer creates intelligent features.

---

# Tax Features

## expected\_tax

```python
expected_tax = subtotal * tax_rate
```

Used to validate:

```text
tax_amount_mismatch
```

---

# tax\_difference

Difference between:

```text
actual tax amount
vs
expected tax amount
```

This helps the ML model detect anomalies.

---

# Currency Support Feature

Checks whether the invoice currency is supported by the target format.

Example:

```text
Currency = INR
Target Format Supports = EUR, USD
```

Result:

```text
currency_not_supported
```

---

# JSON Feature Extraction

Invoices contain:

```text
line_items_json
```

The system extracts:

| Feature              | Meaning               |
| -------------------- | --------------------- |
| line\_item\_count    | number of items       |
| total\_quantity      | total quantity sold   |
| avg\_item\_price     | average product price |
| has\_negative\_price | detects credit notes  |

These features improve anomaly detection.

---

# Missing Value Features

The project creates binary missing indicators:

| Feature                     |
| --------------------------- |
| seller\_vat\_missing        |
| buyer\_vat\_missing         |
| payment\_reference\_missing |
| delivery\_date\_missing     |

This helps the model identify:

```text
missing_required_field
```

---

# Machine Learning Layer

# predict.py

Purpose:

Predict:

1. Whether invoice mapping is valid
2. What errors exist in the invoice

---

# Model Used

The project uses:

# XGBoost Multi-Output Classification

Reason:

- high accuracy
- supports tabular data well
- strong anomaly detection
- handles complex feature relationships
- fast inference

---

# Prediction Targets

The model predicts:

| Target                              |
| ----------------------------------- |
| is\_mapping\_valid                  |
| buyer\_vat\_missing\_for\_target    |
| credit\_note\_not\_supported        |
| currency\_not\_supported            |
| line\_item\_structure\_incompatible |
| missing\_required\_field            |
| seller\_vat\_format\_invalid        |
| tax\_amount\_mismatch               |

This allows multiple errors to exist simultaneously.

---

# prediction\_output.csv

Generated after prediction.

Contains:

| Column             | Meaning            |
| ------------------ | ------------------ |
| invoice\_id        | invoice identifier |
| is\_mapping\_valid | 0 or 1             |
| mapping\_errors    | detected errors    |

Example:

```text
INV001,tax_amount_mismatch,currency_not_supported
```

---

# Deterministic Correction Engine

# correction.py

Purpose:

Automatically repair detected invoice problems.

This module uses deterministic business logic.

No ML is used here.

---

# Why Deterministic Logic?

Invoice systems require:

- explainability
- predictable behavior
- government compliance
- auditability

Therefore corrections are rule-based.

---

# Error Handling Logic

---

# 1. missing\_required\_field

The engine dynamically reads:

```text
required_fields
```

from:

```text
format_rules.csv
```

If required fields are missing:

```text
MISSING
```

is inserted.

Example:

```text
buyer_vat = MISSING
```

---

# 2. tax\_amount\_mismatch

Tax is recalculated:

```python
correct_tax = subtotal * tax_rate
```

Then:

```python
total_amount = subtotal + tax_amount
```

is updated.

---

# 3. currency\_not\_supported

The system:

- fetches live exchange rates
- converts all monetary values
- updates line item prices
- changes invoice currency

Uses:

```text
forex-python
```

Converted fields:

- subtotal
- tax\_amount
- total\_amount
- line item prices

---

# 4. line\_item\_structure\_incompatible

Transforms invoice line structure.

Example:

```text
Flat Structure
    ↓
Nested Structure
```

or vice versa.

This enables transcoding across invoice standards.

---

# 5. buyer\_vat\_missing\_for\_target

Missing VAT values become:

```text
MISSING
```

---

# 6. seller\_vat\_format\_invalid

Invalid VAT values become:

```text
INVALID
```

---

# 7. credit\_note\_not\_supported

Negative invoices are normalized.

The system recalculates:

- subtotal
- tax\_amount
- total\_amount

---

# corrected\_invoice.csv (canonical format)

Generated after corrections.

Contains:

- corrected invoice data
- corrected\_fields column

Example:

```json
{
  "tax_amount": 230,
  "currency": "EUR"
}
```

This creates a complete audit trail.

---

# Dynamic Invoice Transcoder

# mapper.py

Purpose:

Convert corrected canonical invoices into target invoice formats.

This is the core transcoding engine.

---

# Dynamic Rule-Based Mapping

The mapper dynamically reads:

```text
format_rules.csv
```

No hardcoded format conversion is used.

The mapper automatically handles:

- required fields
- optional fields
- VAT field names
- line item structure
- syntax type
- credit note support

---

# Dynamic Target Format Detection

The mapper derives:

```text
target_format
```

using:

```text
target_country
```

and:

```text
used_in_countries
```

from:

```text
format_rules.csv
```

---

# Example Mapping

Canonical invoice:

| Field       |
| ----------- |
| seller\_vat |
| subtotal    |

Target format may require:

| Target Field  |
| ------------- |
| CompanyID     |
| PayableAmount |

The mapper dynamically transforms the structure.

---

# Line Item Transformation

Depending on:

```text
line_item_structure
```

in:

```text
format_rules.csv
```

The system creates:

## Flat structures

or

## Nested structures

---

# Multi-Format Output Support

The system supports:

| Input | Output     |
| ----- | ---------- |
| CSV   | CSV        |
| JSON  | CSV + JSON |
| XML   | CSV + XML  |

---

# final\_mapped\_invoice.csv

Final transcoded invoice output.

Contains invoices converted into target format structures.

---

# final\_mapped\_invoice.json

Generated for JSON inputs.

Contains nested transcoded invoice objects.

---

# final\_mapped\_invoice.xml

Generated for XML inputs.

Contains XML-transcoded invoice structure.

---

# Final Generated Outputs

The pipeline generates:

| File                        | Purpose                     |
| --------------------------- | --------------------------- |
| prediction\_output.csv      | detected anomalies          |
| corrected\_invoice.csv      | corrected canonical invoice |
| final\_mapped\_invoice.csv  | transcoded invoice output   |
| final\_mapped\_invoice.json | JSON output                 |
| final\_mapped\_invoice.xml  | XML output                  |

---

# Technologies Used

| Technology   | Purpose              |
| ------------ | -------------------- |
| Python       | backend processing   |
| Pandas       | dataframe operations |
| Scikit-learn | preprocessing        |
| XGBoost      | anomaly detection    |
| Joblib       | model persistence    |
| xmltodict    | XML parsing          |
| forex-python | currency conversion  |

---

# requirements.txt

```text
pandas
numpy
scikit-learn
xgboost
joblib
xmltodict
forex-python
```

---

# Final System Capabilities

The system supports:

✅ Multi-format invoice input

✅ Intelligent anomaly detection

✅ Multi-label error prediction

✅ Deterministic correction engine

✅ Dynamic currency conversion

✅ Rule-based transcoding

✅ Dynamic invoice structure transformation

✅ Multi-format invoice output generation

✅ Audit trail through corrected\_fields

✅ Enterprise-style modular architecture

---

# End-to-End Example

```text
XML Invoice
      ↓
Converted To CSV
      ↓
Feature Engineering
      ↓
ML Error Detection
      ↓
Tax + Currency Corrections
      ↓
Target Format Mapping
      ↓
PEPPOL / FACTUR-X / PINT 
```
