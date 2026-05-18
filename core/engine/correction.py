# =========================================================
# correction.py
# Complete Intelligent Correction Engine
# =========================================================

import pandas as pd
import json
import uuid
from datetime import datetime
from forex_python.converter import CurrencyRates
from .paths import get_data_path

# =========================================================
# LOAD FORMAT RULES
# =========================================================

format_df = pd.read_csv(
    get_data_path('format_rules.csv')
)
format_df.columns = [str(col).strip().lower() for col in format_df.columns]

def get_realistic_default(field, row, target_format):
    """Generate a realistic value for a missing field."""
    if field == 'invoice_id':
        return f"COR-{uuid.uuid4().hex[:8].upper()}"
    if field == 'issue_date':
        return datetime.now().strftime('%Y-%m-%d')
    if field == 'delivery_date':
        return (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    if field == 'seller_id' or field == 'buyer_id':
        country = row.get('target_country', 'XX')
        return f"{country}-{random.randint(1000, 9999)}"
    if field == 'payment_reference':
        return f"PAY-{uuid.uuid4().hex[:6].upper()}"
    return "N/A"

# =========================================================
# MAIN CORRECTION FUNCTION
# =========================================================

def correct_invoice(

    original_invoice_path,
    prediction_output_path

):
    import random
    from datetime import timedelta

    # =====================================================
    # LOAD FILES
    # =====================================================

    invoice_df = pd.read_csv(
        original_invoice_path
    )

    prediction_df = pd.read_csv(
        prediction_output_path
    )

    # =====================================================
    # CREATE COPY
    # =====================================================

    corrected_df = invoice_df.copy()

    # =====================================================
    # STORE CORRECTED FIELD CHANGES
    # =====================================================

    corrected_fields_list = []

    # =====================================================
    # CURRENCY API
    # =====================================================

    c = CurrencyRates()

    # =====================================================
    # PROCESS EACH ROW
    # =====================================================

    for idx in range(len(corrected_df)):

        errors = str(prediction_df.loc[idx, 'mapping_errors'])
        corrected_fields = {}
        row = corrected_df.iloc[idx]

        # =================================================
        # 1. missing_required_field
        # =================================================

        if 'missing_required_field' in errors:
            target_country = str(row['target_country']).lower()
            target_format = None

            for _, format_rule in format_df.iterrows():
                if target_country in str(format_rule['used_in_countries']).lower():
                    target_format = format_rule['format_id']
                    break

            format_row = format_df[format_df['format_id'] == target_format]
            if not format_row.empty:
                required_fields = [f.strip() for f in str(format_row.iloc[0]['required_fields']).split(',')]

                for field in required_fields:
                    if field in corrected_df.columns:
                        if pd.isnull(corrected_df.loc[idx, field]) or str(corrected_df.loc[idx, field]).strip() == '':
                            default_val = get_realistic_default(field, row, target_format)
                            corrected_df.loc[idx, field] = default_val
                            corrected_fields[field] = default_val

        # =================================================
        # 2. tax_amount_mismatch
        # =================================================

        if 'tax_amount_mismatch' in errors:
            subtotal = corrected_df.loc[idx, 'subtotal']
            tax_rate = corrected_df.loc[idx, 'tax_rate']
            corrected_tax = round(subtotal * tax_rate, 2)
            corrected_total = round(subtotal + corrected_tax, 2)
            
            corrected_df.loc[idx, 'tax_amount'] = corrected_tax
            corrected_df.loc[idx, 'total_amount'] = corrected_total
            corrected_fields['tax_amount'] = corrected_tax
            corrected_fields['total_amount'] = corrected_total

        # =================================================
        # 3. currency_not_supported
        # =================================================

        if 'currency_not_supported' in errors:
            old_currency = corrected_df.loc[idx, 'currency']
            target_country = str(row['target_country']).lower()
            target_format = None

            for _, format_rule in format_df.iterrows():
                if target_country in str(format_rule['used_in_countries']).lower():
                    target_format = format_rule['format_id']
                    break

            if target_format:
                format_row = format_df[format_df['format_id'] == target_format]
                supported = [currency.strip() for currency in str(format_row.iloc[0]['supported_currencies']).split(',')]
                target_currency = supported[0]

                try:
                    conversion_rate = c.get_rate(old_currency, target_currency)
                except Exception as e:
                    print(f"Currency conversion failed: {str(e)}. Defaulting to 1.0")
                    conversion_rate = 1.0

                for field in ['subtotal', 'tax_amount', 'total_amount']:
                    corrected_df.loc[idx, field] = round(float(corrected_df.loc[idx, field]) * conversion_rate, 2)
                    corrected_fields[field] = corrected_df.loc[idx, field]

                corrected_df.loc[idx, 'currency'] = target_currency
                corrected_fields['currency'] = target_currency

        # =================================================
        # 6. seller_vat_format_invalid
        # =================================================

        if 'seller_vat_format_invalid' in errors:
            from core.engine.data_generator import generate_vat
            from core.engine.utils import infer_country_from_vat
            
            old_vat = str(corrected_df.loc[idx, 'seller_vat'])
            country = infer_country_from_vat(old_vat) or str(row['target_country'])
            new_vat = generate_vat(country)
            corrected_df.loc[idx, 'seller_vat'] = new_vat
            corrected_fields['seller_vat'] = new_vat

        # =================================================
        # REST OF ERRORS (Credit Note, Structure)
        # =================================================
        
        # Credit Note
        if 'credit_note_not_supported' in errors:
            val = abs(corrected_df.loc[idx, 'subtotal'])
            corrected_df.loc[idx, 'subtotal'] = val
            corrected_fields['subtotal'] = val
            # Total/Tax also needs abs
            corrected_df.loc[idx, 'tax_amount'] = abs(corrected_df.loc[idx, 'tax_amount'])
            corrected_df.loc[idx, 'total_amount'] = abs(corrected_df.loc[idx, 'total_amount'])

        # Line items structure (Handled during transcoding, but update flag here)
        if 'line_item_structure_incompatible' in errors:
             corrected_fields['structure'] = 'FIXED_DURING_TRANSCODING'

        corrected_fields_list.append(json.dumps(corrected_fields))

    corrected_df['corrected_fields'] = corrected_fields_list
    corrected_df.to_csv('outputs/corrected_invoice.csv', index=False)
    return corrected_df