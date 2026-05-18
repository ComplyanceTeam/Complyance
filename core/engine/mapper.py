# =========================================================
# mapper.py
# Dynamic Rule-Based Invoice Transcoder
# =========================================================

import pandas as pd
import json
import xmltodict
from .paths import get_data_path
from .transcoder import SYNTAX_FIELD_MAPS
from .utils import nest_line_items

# =========================================================
# LOAD FORMAT RULES
# =========================================================

format_df = pd.read_csv(
    get_data_path('format_rules.csv')
)

# =========================================================
# MAIN MAPPING FUNCTION
# =========================================================

def build_nested_dict(flat_dict):
    """Convert flat dict with path keys ('a/b/c') to nested dict."""
    nested = {}
    for key, value in flat_dict.items():
        if '/' in key:
            parts = key.split('/')
            curr = nested
            for part in parts[:-1]:
                if part not in curr:
                    curr[part] = {}
                curr = curr[part]
            curr[parts[-1]] = value
        else:
            nested[key] = value
    return nested

def map_invoice(

    corrected_invoice_path,
    input_file_type

):

    # =====================================================
    # LOAD CORRECTED INVOICE
    # =====================================================

    invoice_df = pd.read_csv(
        corrected_invoice_path
    )

    # =====================================================
    # STORE FINAL MAPPED INVOICES
    # =====================================================

    mapped_invoices = []

    # =====================================================
    # PROCESS EACH INVOICE
    # =====================================================

    for idx in range(len(invoice_df)):

        row = invoice_df.iloc[idx]

        # =================================================
        # GET TARGET FORMAT FROM TARGET COUNTRY
        # =================================================

        target_country = str(
            row['target_country']
        ).lower()

        target_format = None

        for _, format_rule in format_df.iterrows():

            countries = str(

                format_rule[
                    'used_in_countries'
                ]

            ).lower()

            if target_country in countries:

                target_format = format_rule[
                    'format_id'
                ]

                break

        if target_format is None:
            continue

        # =================================================
        # EXTRACT RULES
        # =================================================

        format_row = format_df[
            format_df['format_id'] == target_format
        ].iloc[0]

        syntax = format_row['syntax']
        tax_id_field_name = format_row['tax_id_field_name']
        line_item_structure = format_row['line_item_structure']
        supports_credit_note = format_row['supports_credit_note']

        # Get field map for target syntax
        field_map = SYNTAX_FIELD_MAPS.get(syntax, {})

        # =================================================
        # CREATE TARGET INVOICE OBJECT
        # =================================================

        mapped_invoice = {}
        
        # Add metadata (for internal tracking, usually filtered for final XML)
        if input_file_type == 'json':
            mapped_invoice['_target_format'] = target_format
            mapped_invoice['_syntax'] = syntax

        # Map all standard fields using the syntax map
        standard_fields = [
            'invoice_id', 'seller_id', 'buyer_id', 'issue_date',
            'currency', 'subtotal', 'tax_rate', 'tax_amount',
            'total_amount', 'seller_vat', 'buyer_vat',
            'payment_reference', 'delivery_date'
        ]

        for field in standard_fields:
            # Use mapped name if available, otherwise canonical
            mapped_name = field_map.get(field, field)
            
            # Special case for seller_vat as it has a dynamic target name in format_rules
            if field == 'seller_vat':
                mapped_name = tax_id_field_name
            
            if field in row.index:
                mapped_invoice[mapped_name] = row[field]
            else:
                mapped_invoice[mapped_name] = None

        # =================================================
        # LINE ITEM STRUCTURE TRANSFORMATION
        # =================================================

        try:
            line_data = json.loads(row['line_items_json'])
        except:
            line_data = []

        target_line_items = line_data
        
        # FLAT → NESTED
        if isinstance(line_data, list) and line_item_structure == 'nested':
            target_line_items = nest_line_items(line_data)
        
        # NESTED → FLAT
        elif isinstance(line_data, dict) and 'invoice_lines' in line_data and line_item_structure == 'flat':
            items = line_data['invoice_lines']
            flattened = []
            for item in items:
                details = item.get('line', {}).get('item_details', item)
                flattened.append({
                    'description': details.get('description', 'UNKNOWN'),
                    'price': details.get('price', 0),
                    'qty': details.get('qty', 1)
                })
            target_line_items = flattened

        # Map line items key
        line_items_key = field_map.get('line_items_json', 'line_items')
        mapped_invoice[line_items_key] = target_line_items

        # =================================================
        # XML STRUCTURING (if output is XML)
        # =================================================
        
        if input_file_type == 'xml':
            # Turn flat path keys into actual XML hierarchy
            mapped_invoice = build_nested_dict(mapped_invoice)

        # =================================================
        # SAVE CURRENT INVOICE
        # =================================================

        mapped_invoices.append(mapped_invoice)

    # =====================================================
    # CREATE FINAL DATAFRAME (for CSV)
    # =====================================================
    
    # Flatten everything for CSV output
    final_df = pd.json_normalize(mapped_invoices)

    # =====================================================
    # ALWAYS SAVE CSV
    # =====================================================

    final_df.to_csv(

        'outputs/final_mapped_invoice.csv',

        index=False
    )

    print(
        "\nCSV Output Saved Successfully"
    )

    # =====================================================
    # JSON OUTPUT
    # =====================================================

    if input_file_type == 'json':

        with open(

            'outputs/final_mapped_invoice.json',

            'w',

            encoding='utf-8'

        ) as json_file:

            json.dump(

                mapped_invoices,

                json_file,

                indent=4
            )

        print(
            "JSON Output Saved Successfully"
        )

    # =====================================================
    # XML OUTPUT
    # =====================================================

    elif input_file_type == 'xml':

        # Wrap in a standard envelope
        root_tag = 'Invoice' if syntax == 'UBL' else 'CrossIndustryInvoice'

        if len(mapped_invoices) == 1:
            xml_data = {root_tag: mapped_invoices[0]}
        else:
            # Ensure a single root element for multiple invoices
            xml_data = {'Invoices': {root_tag: mapped_invoices}}

        xml_string = xmltodict.unparse(

            xml_data,

            pretty=True
        )

        with open(

            'outputs/final_mapped_invoice.xml',

            'w',

            encoding='utf-8'

        ) as xml_file:

            xml_file.write(xml_string)

        print(
            "XML Output Saved Successfully"
        )

    # =====================================================
    # FINAL MESSAGE
    # =====================================================

    print(
        "\nFinal Invoice Transcoding Completed"
    )

    return final_df