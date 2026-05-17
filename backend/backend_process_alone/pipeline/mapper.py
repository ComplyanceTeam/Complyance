# =========================================================
# mapper.py
# Dynamic Rule-Based Invoice Transcoder
# =========================================================

import pandas as pd
import json
import xmltodict

# =========================================================
# LOAD FORMAT RULES
# =========================================================

format_df = pd.read_csv(
    'data/format_rules.csv'
)

# =========================================================
# MAIN MAPPING FUNCTION
# =========================================================

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

        # -------------------------------------------------
        # Skip if no format found
        # -------------------------------------------------

        if target_format is None:

            continue

        # =================================================
        # EXTRACT RULES
        # =================================================

        format_row = format_df[

            format_df['format_id']
            == target_format

        ].iloc[0]

        syntax = format_row['syntax']

        required_fields = [

            field.strip()

            for field in str(
                format_row[
                    'required_fields'
                ]
            ).split(',')
        ]

        optional_fields = [

            field.strip()

            for field in str(
                format_row[
                    'optional_fields'
                ]
            ).split(',')
        ]

        tax_id_field_name = (

            format_row[
                'tax_id_field_name'
            ]
        )

        line_item_structure = (

            format_row[
                'line_item_structure'
            ]
        )

        supports_credit_note = (

            format_row[
                'supports_credit_note'
            ]
        )

        # =================================================
        # CREATE TARGET INVOICE OBJECT
        # =================================================

        mapped_invoice = {}

        # -------------------------------------------------
        # Metadata
        # -------------------------------------------------

        mapped_invoice[
            'target_format'
        ] = target_format

        mapped_invoice[
            'syntax'
        ] = syntax

        mapped_invoice[
            'line_item_structure'
        ] = line_item_structure

        # =================================================
        # REQUIRED FIELDS
        # =================================================

        for field in required_fields:

            if field in row.index:

                mapped_invoice[field] = row[field]

            else:

                mapped_invoice[field] = 'MISSING'

        # =================================================
        # OPTIONAL FIELDS
        # =================================================

        for field in optional_fields:

            if field in row.index:

                mapped_invoice[field] = row[field]

        # =================================================
        # VAT FIELD TRANSFORMATION
        # =================================================

        if 'seller_vat' in row.index:

            mapped_invoice[
                tax_id_field_name
            ] = row['seller_vat']

        # =================================================
        # LINE ITEM STRUCTURE TRANSFORMATION
        # =================================================

        try:

            line_json = json.loads(
                row['line_items_json']
            )

        except:

            line_json = {}

        # -------------------------------------------------
        # FLAT STRUCTURE
        # -------------------------------------------------

        if line_item_structure == 'flat':

            flattened_items = []

            if 'invoice_lines' in line_json:

                for item in line_json[
                    'invoice_lines'
                ]:

                    flat_item = {

                        'description':

                        item.get(
                            'line',
                            {}
                        ).get(
                            'item_details',
                            {}
                        ).get(
                            'description',
                            'UNKNOWN'
                        ),

                        'price':

                        item.get(
                            'line',
                            {}
                        ).get(
                            'item_details',
                            {}
                        ).get(
                            'price',
                            0
                        ),

                        'qty':

                        item.get(
                            'line',
                            {}
                        ).get(
                            'item_details',
                            {}
                        ).get(
                            'qty',
                            1
                        )
                    }

                    flattened_items.append(
                        flat_item
                    )

            mapped_invoice[
                'line_items'
            ] = flattened_items

        # -------------------------------------------------
        # NESTED STRUCTURE
        # -------------------------------------------------

        else:

            mapped_invoice[
                'line_items'
            ] = line_json

        # =================================================
        # CREDIT NOTE VALIDATION
        # =================================================

        subtotal = row.get(
            'subtotal',
            0
        )

        if (

            subtotal < 0
            and
            supports_credit_note == 0

        ):

            mapped_invoice[
                'credit_note_status'
            ] = 'NOT_SUPPORTED'

        else:

            mapped_invoice[
                'credit_note_status'
            ] = 'SUPPORTED'

        # =================================================
        # CURRENCY
        # =================================================

        mapped_invoice[
            'currency'
        ] = row['currency']

        # =================================================
        # SAVE CURRENT INVOICE
        # =================================================

        mapped_invoices.append(
            mapped_invoice
        )

    # =====================================================
    # CREATE FINAL DATAFRAME
    # =====================================================

    final_df = pd.json_normalize(
        mapped_invoices
    )

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

        xml_data = {

            'Invoices': {

                'Invoice': mapped_invoices
            }
        }

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