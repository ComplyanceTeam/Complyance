"""
Configuration constants for the E-Invoice Format Transcoder.
Based on real-world e-invoicing standards (Peppol BIS 3.0, XRechnung, Factur-X, PINT, etc.)
"""

# ─────────────────────────────────────────────────────────
# FORMAT RULES — mirrors format_rules.csv
# ─────────────────────────────────────────────────────────
FORMAT_RULES = [
    {
        "format_id": 1,
        "format_name": "peppol_bis_3",
        "used_in_countries": "BE,AT,IT,FI,NO,SE",
        "syntax": "UBL",
        "required_fields": "invoice_id,seller_id,buyer_id,issue_date,currency,subtotal,tax_rate,tax_amount,total_amount,line_items_json,seller_vat,buyer_vat,payment_reference",
        "optional_fields": "delivery_date",
        "tax_id_field_name": "AccountingSupplierParty/PartyTaxScheme/CompanyID",
        "line_item_structure": "nested",
        "supports_credit_note": True,
        "max_line_items": 999,
    },
    {
        "format_id": 2,
        "format_name": "xrechnung_ubl",
        "used_in_countries": "DE",
        "syntax": "UBL",
        "required_fields": "invoice_id,seller_id,buyer_id,issue_date,currency,subtotal,tax_rate,tax_amount,total_amount,line_items_json,seller_vat,buyer_vat,delivery_date",
        "optional_fields": "payment_reference",
        "tax_id_field_name": "AccountingSupplierParty/PartyTaxScheme/CompanyID",
        "line_item_structure": "nested",
        "supports_credit_note": True,
        "max_line_items": 500,
    },
    {
        "format_id": 3,
        "format_name": "xrechnung_cii",
        "used_in_countries": "DE",
        "syntax": "CII",
        "required_fields": "invoice_id,seller_id,buyer_id,issue_date,currency,subtotal,tax_rate,tax_amount,total_amount,line_items_json,seller_vat,buyer_vat",
        "optional_fields": "payment_reference,delivery_date",
        "tax_id_field_name": "SellerTradeParty/SpecifiedTaxRegistration/ID",
        "line_item_structure": "flat",
        "supports_credit_note": True,
        "max_line_items": 500,
    },
    {
        "format_id": 4,
        "format_name": "zugferd",
        "used_in_countries": "DE,AT,CH",
        "syntax": "CII",
        "required_fields": "invoice_id,seller_id,buyer_id,issue_date,currency,subtotal,tax_rate,tax_amount,total_amount,line_items_json,seller_vat",
        "optional_fields": "buyer_vat,payment_reference,delivery_date",
        "tax_id_field_name": "SellerTradeParty/SpecifiedTaxRegistration/ID",
        "line_item_structure": "flat",
        "supports_credit_note": True,
        "max_line_items": 200,
    },
    {
        "format_id": 5,
        "format_name": "facturx",
        "used_in_countries": "FR",
        "syntax": "CII",
        "required_fields": "invoice_id,seller_id,buyer_id,issue_date,currency,subtotal,tax_rate,tax_amount,total_amount,line_items_json,seller_vat,delivery_date",
        "optional_fields": "buyer_vat,payment_reference",
        "tax_id_field_name": "SellerTradeParty/SpecifiedTaxRegistration/ID",
        "line_item_structure": "flat",
        "supports_credit_note": False,
        "max_line_items": 200,
    },
    {
        "format_id": 6,
        "format_name": "pint_my",
        "used_in_countries": "MY",
        "syntax": "UBL",
        "required_fields": "invoice_id,seller_id,buyer_id,issue_date,currency,subtotal,tax_rate,tax_amount,total_amount,line_items_json,seller_vat",
        "optional_fields": "buyer_vat,payment_reference,delivery_date",
        "tax_id_field_name": "AccountingSupplierParty/PartyTaxScheme/CompanyID",
        "line_item_structure": "flat",
        "supports_credit_note": False,
        "max_line_items": 100,
    },
    {
        "format_id": 7,
        "format_name": "pint_sg",
        "used_in_countries": "SG",
        "syntax": "UBL",
        "required_fields": "invoice_id,seller_id,buyer_id,issue_date,currency,subtotal,tax_rate,tax_amount,total_amount,line_items_json,seller_vat,buyer_vat,delivery_date",
        "optional_fields": "payment_reference",
        "tax_id_field_name": "AccountingSupplierParty/PartyTaxScheme/CompanyID",
        "line_item_structure": "nested",
        "supports_credit_note": True,
        "max_line_items": 100,
    },
    {
        "format_id": 8,
        "format_name": "nlcius",
        "used_in_countries": "NL",
        "syntax": "UBL",
        "required_fields": "invoice_id,seller_id,buyer_id,issue_date,currency,subtotal,tax_rate,tax_amount,total_amount,line_items_json,seller_vat,buyer_vat,payment_reference",
        "optional_fields": "delivery_date",
        "tax_id_field_name": "AccountingSupplierParty/PartyTaxScheme/CompanyID",
        "line_item_structure": "nested",
        "supports_credit_note": True,
        "max_line_items": 500,
    },
]

# Quick lookup dicts
FORMAT_BY_NAME = {f["format_name"]: f for f in FORMAT_RULES}
FORMAT_BY_ID = {f["format_id"]: f for f in FORMAT_RULES}

# ─────────────────────────────────────────────────────────
# COUNTRY → DEFAULT TARGET FORMAT
# ─────────────────────────────────────────────────────────
COUNTRY_FORMAT_MAP = {
    "DE": "xrechnung_ubl",
    "FR": "facturx",
    "MY": "pint_my",
    "SG": "pint_sg",
    "BE": "peppol_bis_3",
    "NL": "nlcius",
    "AT": "peppol_bis_3",
    "IT": "peppol_bis_3",
    "FI": "peppol_bis_3",
    "NO": "peppol_bis_3",
    "SE": "peppol_bis_3",
    "CH": "zugferd",
}

# ─────────────────────────────────────────────────────────
# SUPPORTED CURRENCIES PER FORMAT
# ─────────────────────────────────────────────────────────
FORMAT_CURRENCIES = {
    "peppol_bis_3":  ["EUR", "GBP", "SEK", "DKK", "NOK"],
    "xrechnung_ubl": ["EUR"],
    "xrechnung_cii": ["EUR"],
    "zugferd":       ["EUR", "CHF"],
    "facturx":       ["EUR"],
    "pint_my":       ["MYR", "USD"],
    "pint_sg":       ["SGD", "USD"],
    "nlcius":        ["EUR"],
}

# ─────────────────────────────────────────────────────────
# VAT NUMBER REGEX PATTERNS (real-world formats)
# ─────────────────────────────────────────────────────────
VAT_PATTERNS = {
    "DE": r"^DE\d{9}$",
    "FR": r"^FR[A-Z0-9]{2}\d{9}$",
    "BE": r"^BE0\d{9}$",
    "NL": r"^NL\d{9}B\d{2}$",
    "MY": r"^MY\d{10,12}$",
    "SG": r"^SG\d{9}[A-Z]$",
    "AT": r"^ATU\d{8}$",
    "IT": r"^IT\d{11}$",
    "FI": r"^FI\d{8}$",
    "NO": r"^NO\d{9}MVA$",
    "SE": r"^SE\d{12}$",
    "CH": r"^CHE\d{9}$",
}

# ─────────────────────────────────────────────────────────
# STANDARD TAX RATES PER COUNTRY (real rates as of 2024)
# ─────────────────────────────────────────────────────────
STANDARD_TAX_RATES = {
    "DE": [0.19, 0.07],          # Standard / Reduced
    "FR": [0.20, 0.10, 0.055],   # Standard / Intermediate / Reduced
    "BE": [0.21, 0.12, 0.06],
    "NL": [0.21, 0.09],
    "MY": [0.06, 0.10, 0.0],     # SST rates + exempt
    "SG": [0.09, 0.0],           # GST + exempt
    "AT": [0.20, 0.10, 0.13],
    "IT": [0.22, 0.10, 0.04],
    "FI": [0.255, 0.14, 0.10],
    "NO": [0.25, 0.15, 0.12],
    "SE": [0.25, 0.12, 0.06],
    "CH": [0.081, 0.026, 0.0],
}

# Default currencies per country (what sellers typically invoice in)
COUNTRY_CURRENCIES = {
    "DE": "EUR", "FR": "EUR", "BE": "EUR", "NL": "EUR",
    "AT": "EUR", "IT": "EUR", "FI": "EUR",
    "NO": "NOK", "SE": "SEK",
    "MY": "MYR", "SG": "SGD", "CH": "CHF",
}

# ─────────────────────────────────────────────────────────
# TRADE CORRIDORS — weighted source→target country pairs
# Reflects real-world cross-border trading patterns
# ─────────────────────────────────────────────────────────
TRADE_CORRIDORS = [
    # (source_format, target_country, weight) — weight determines frequency
    # EU internal — high volume
    ("xrechnung_ubl", "FR", 15),   # DE→FR
    ("xrechnung_ubl", "NL", 12),   # DE→NL
    ("xrechnung_ubl", "BE", 10),   # DE→BE
    ("xrechnung_cii", "FR", 8),    # DE(CII)→FR
    ("xrechnung_cii", "NL", 6),    # DE(CII)→NL
    ("facturx", "BE", 12),         # FR→BE
    ("facturx", "DE", 10),         # FR→DE
    ("facturx", "NL", 6),          # FR→NL
    ("peppol_bis_3", "DE", 10),    # BE/AT/IT→DE
    ("peppol_bis_3", "FR", 8),     # BE/AT/IT→FR
    ("peppol_bis_3", "NL", 6),     # BE/AT/IT→NL
    ("nlcius", "DE", 10),          # NL→DE
    ("nlcius", "BE", 8),           # NL→BE
    ("nlcius", "FR", 5),           # NL→FR
    ("zugferd", "FR", 6),          # DE/AT/CH→FR
    ("zugferd", "BE", 6),          # DE/AT/CH→BE
    ("zugferd", "NL", 5),          # DE/AT/CH→NL
    # ASEAN corridors
    ("pint_my", "SG", 10),         # MY→SG
    ("pint_my", "DE", 4),          # MY→DE (export)
    ("pint_sg", "MY", 10),         # SG→MY
    ("pint_sg", "DE", 4),          # SG→DE (export)
    # Cross-region
    ("xrechnung_ubl", "MY", 3),    # DE→MY
    ("xrechnung_ubl", "SG", 3),    # DE→SG
    ("peppol_bis_3", "SG", 3),     # EU→SG
    ("facturx", "SG", 2),          # FR→SG
]

# ─────────────────────────────────────────────────────────
# REALISTIC PRODUCT CATALOGS (by industry sector)
# ─────────────────────────────────────────────────────────
PRODUCT_CATALOG = {
    "manufacturing": [
        ("Hydraulic Cylinder HZ-400", 245.00, "EA"),
        ("Steel Sheet 2mm 1000x2000mm", 89.50, "EA"),
        ("Ball Bearing SKF 6205-2RS", 12.40, "EA"),
        ("CNC Machining Service", 150.00, "HUR"),
        ("Aluminum Extrusion Profile 40x40", 34.20, "MTR"),
        ("Industrial Gasket Set DN50", 28.75, "EA"),
        ("Stainless Steel Bolt M12x60", 1.85, "EA"),
        ("Pneumatic Actuator DA-63", 312.00, "EA"),
        ("Welding Wire 1.2mm 15kg", 67.90, "EA"),
        ("Precision Ground Shaft 25mm", 94.30, "MTR"),
    ],
    "it_services": [
        ("Cloud Hosting Monthly", 499.00, "EA"),
        ("Software License Enterprise Annual", 2400.00, "EA"),
        ("IT Consultation", 185.00, "HUR"),
        ("Server Rack Unit 42U", 1250.00, "EA"),
        ("SSD 1TB NVMe Enterprise", 189.00, "EA"),
        ("Network Switch 48-Port PoE+", 845.00, "EA"),
        ("Cybersecurity Audit", 3500.00, "EA"),
        ("Data Migration Service", 275.00, "HUR"),
        ("CAT6A Cable 305m Box", 198.00, "EA"),
        ("UPS 3000VA Rackmount", 1120.00, "EA"),
    ],
    "office_supplies": [
        ("A4 Paper Premium 80gsm 500-Sheet", 5.90, "EA"),
        ("Toner Cartridge Black HP 26A", 78.50, "EA"),
        ("Ergonomic Office Chair Pro", 445.00, "EA"),
        ("Standing Desk Electric 160x80", 629.00, "EA"),
        ("Whiteboard Magnetic 120x90cm", 89.00, "EA"),
        ("Document Shredder Cross-Cut", 199.00, "EA"),
        ("Monitor Arm Dual VESA", 79.90, "EA"),
        ("Desk Organizer Set 5-Piece", 34.50, "EA"),
        ("LED Desk Lamp Adjustable", 45.00, "EA"),
        ("Filing Cabinet 4-Drawer Steel", 265.00, "EA"),
    ],
    "electronics": [
        ("PCB Assembly 4-Layer", 8.50, "EA"),
        ("LCD Display Module 7-inch", 42.00, "EA"),
        ("Microcontroller STM32F407", 11.20, "EA"),
        ("Power Supply Module 24V/10A", 68.00, "EA"),
        ("Capacitor 100uF 50V MLCC", 0.15, "EA"),
        ("Connector USB-C Female PCB", 1.20, "EA"),
        ("Heat Sink Aluminum 40x40x20", 3.80, "EA"),
        ("Wire Harness Custom 12-Pin", 15.60, "EA"),
        ("EMI Shielding Gasket 100mm", 7.40, "EA"),
        ("Thermal Paste Arctic MX-6 4g", 9.90, "EA"),
    ],
    "professional_services": [
        ("Legal Consultation", 320.00, "HUR"),
        ("Annual Financial Audit", 8500.00, "EA"),
        ("Translation Service EN-DE", 0.12, "EA"),
        ("Patent Filing Service", 4200.00, "EA"),
        ("Market Research Report", 6800.00, "EA"),
        ("HR Recruitment Service", 3500.00, "EA"),
        ("Tax Advisory Session", 250.00, "HUR"),
        ("Compliance Training Workshop", 1800.00, "EA"),
        ("Business Process Consulting", 275.00, "HUR"),
        ("Quality Management Certification", 5200.00, "EA"),
    ],
}

# ─────────────────────────────────────────────────────────
# REALISTIC COMPANY NAMES BY COUNTRY
# ─────────────────────────────────────────────────────────
COMPANIES = {
    "DE": [
        ("Müller Maschinenbau GmbH", "DE"),
        ("Schmidt Elektronik AG", "DE"),
        ("Weber Metallverarbeitung KG", "DE"),
        ("Fischer Industrietechnik GmbH", "DE"),
        ("Bauer Präzisionsteile GmbH", "DE"),
        ("Hoffmann Systemtechnik AG", "DE"),
        ("Schneider Automotive GmbH", "DE"),
        ("Krüger Werkzeugbau GmbH", "DE"),
    ],
    "FR": [
        ("Dupont Industries SA", "FR"),
        ("Lefebvre Mécanique SARL", "FR"),
        ("Martin Technologies SAS", "FR"),
        ("Bernard Électronique SA", "FR"),
        ("Moreau Services Conseil SARL", "FR"),
        ("Petit Fournitures SAS", "FR"),
    ],
    "BE": [
        ("Janssens Engineering NV", "BE"),
        ("Peeters Logistics BVBA", "BE"),
        ("Van den Berg Technologie NV", "BE"),
        ("Claes Manufacturing NV", "BE"),
    ],
    "NL": [
        ("De Vries Techniek BV", "NL"),
        ("Bakker Trading BV", "NL"),
        ("Visser Machinefabriek BV", "NL"),
        ("Smit & Zonen BV", "NL"),
        ("Dijkstra Elektro BV", "NL"),
    ],
    "MY": [
        ("Wira Tech Solutions Sdn Bhd", "MY"),
        ("Perdana Manufacturing Sdn Bhd", "MY"),
        ("Bestari Components Sdn Bhd", "MY"),
        ("Harmoni Electronics Sdn Bhd", "MY"),
    ],
    "SG": [
        ("Temasek Precision Pte Ltd", "SG"),
        ("Lion City Electronics Pte Ltd", "SG"),
        ("Orchid Systems Pte Ltd", "SG"),
        ("Meridian Solutions Pte Ltd", "SG"),
    ],
    "AT": [
        ("Steiner Maschinenbau GmbH", "AT"),
        ("Huber Technik GesmbH", "AT"),
        ("Gruber Metallwaren GmbH", "AT"),
    ],
    "IT": [
        ("Rossi Meccanica SRL", "IT"),
        ("Bianchi Automazione SpA", "IT"),
        ("Conti Elettronica SRL", "IT"),
    ],
    "CH": [
        ("Zürcher Präzision AG", "CH"),
        ("Berner Technik GmbH", "CH"),
    ],
}

# ─────────────────────────────────────────────────────────
# MAPPING ERROR TYPES (as specified in problem statement)
# ─────────────────────────────────────────────────────────
ERROR_TYPES = [
    "missing_required_field",
    "tax_amount_mismatch",
    "currency_not_supported",
    "line_item_structure_incompatible",
    "buyer_vat_missing_for_target",
    "seller_vat_format_invalid",
    "credit_note_not_supported",
]

# Target error distribution (of the ~20% error invoices)
ERROR_WEIGHTS = {
    "tax_amount_mismatch": 25,
    "missing_required_field": 20,
    "seller_vat_format_invalid": 15,
    "buyer_vat_missing_for_target": 15,
    "currency_not_supported": 10,
    "line_item_structure_incompatible": 10,
    "credit_note_not_supported": 5,
}
