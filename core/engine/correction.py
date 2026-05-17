# =========================================================
# correction.py
# Complete Intelligent Correction Engine
# =========================================================

import pandas as pd
import json

from forex_python.converter import CurrencyRates
from .paths import get_data_path

# =========================================================
# LOAD FORMAT RULES
# =========================================================

format_df = pd.read_csv(
    get_data_path('format_rules.csv')
)

# =========================================================
# MAIN CORRECTION FUNCTION
# =========================================================

def correct_invoice(

    original_invoice_path,
    prediction_output_path

):

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

        # -------------------------------------------------
        # Current Errors
        # -------------------------------------------------

        errors = str(
            prediction_df.loc[idx, 'mapping_errors']
        )

        corrected_fields = {}

        # =================================================
        # 1. missing_required_field
        # =================================================

        if 'missing_required_field' in errors:

            # ---------------------------------------------
            # FIND TARGET FORMAT USING TARGET COUNTRY
            # ---------------------------------------------

            target_country = str(
                corrected_df.loc[
                    idx,
                    'target_country'
                ]
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

            # ---------------------------------------------
            # FIND FORMAT RULE
            # ---------------------------------------------

            format_row = format_df[

                format_df['format_id']
                == target_format
            ]

            if not format_row.empty:

                required_fields_string = (

                    format_row.iloc[0][
                        'required_fields'
                    ]
                )

                required_fields = [

                    field.strip()

                    for field in str(
                        required_fields_string
                    ).split(',')
                ]

                # -----------------------------------------
                # CHECK REQUIRED FIELDS
                # -----------------------------------------

                for field in required_fields:

                    if field in corrected_df.columns:

                        value = corrected_df.loc[
                            idx,
                            field
                        ]

                        if (

                            pd.isnull(value)

                            or

                            str(value).strip() == ''

                        ):

                            corrected_df.loc[
                                idx,
                                field
                            ] = 'MISSING'

                            corrected_fields[field] = (
                                'MISSING'
                            )

        # =================================================
        # 2. tax_amount_mismatch
        # =================================================

        if 'tax_amount_mismatch' in errors:

            subtotal = corrected_df.loc[
                idx,
                'subtotal'
            ]

            tax_rate = corrected_df.loc[
                idx,
                'tax_rate'
            ]

            corrected_tax = round(
                subtotal * tax_rate,
                2
            )

            corrected_total = round(
                subtotal + corrected_tax,
                2
            )

            corrected_df.loc[
                idx,
                'tax_amount'
            ] = corrected_tax

            corrected_df.loc[
                idx,
                'total_amount'
            ] = corrected_total

            corrected_fields[
                'tax_amount'
            ] = corrected_tax

            corrected_fields[
                'total_amount'
            ] = corrected_total

        # =================================================
        # 3. currency_not_supported
        # =================================================

        if 'currency_not_supported' in errors:

            old_currency = corrected_df.loc[
                idx,
                'currency'
            ]

            # ---------------------------------------------
            # FIND TARGET FORMAT USING TARGET COUNTRY
            # ---------------------------------------------

            target_country = str(
                corrected_df.loc[
                    idx,
                    'target_country'
                ]
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

            # ---------------------------------------------
            # SKIP IF FORMAT NOT FOUND
            # ---------------------------------------------

            if target_format is None:

                continue

            # ---------------------------------------------
            # GET TARGET FORMAT RULE
            # ---------------------------------------------

            format_row = format_df[

                format_df['format_id']
                == target_format
            ]

            # ---------------------------------------------
            # GET SUPPORTED CURRENCIES
            # ---------------------------------------------

            supported_currencies = str(

                format_row.iloc[0][
                    'supported_currencies'
                ]

            ).split(',')

            supported_currencies = [

                curr.strip()

                for curr in supported_currencies
            ]

            # ---------------------------------------------
            # PICK FIRST SUPPORTED CURRENCY
            # ---------------------------------------------

            target_currency = supported_currencies[0]

            # ---------------------------------------------
            # FETCH LIVE EXCHANGE RATE
            # ---------------------------------------------

            try:

                conversion_rate = c.get_rate(

                    old_currency,
                    target_currency
                )

            except:

                conversion_rate = 1

            # ---------------------------------------------
            # CONVERT MONETARY FIELDS
            # ---------------------------------------------

            money_fields = [

                'subtotal',
                'tax_amount',
                'total_amount'
            ]

            for field in money_fields:

                if field in corrected_df.columns:

                    old_value = corrected_df.loc[
                        idx,
                        field
                    ]

                    try:

                        new_value = round(

                            float(old_value)
                            * conversion_rate,

                            2
                        )

                        corrected_df.loc[
                            idx,
                            field
                        ] = new_value

                        corrected_fields[field] = (
                            new_value
                        )

                    except:

                        pass

            # ---------------------------------------------
            # UPDATE CURRENCY
            # ---------------------------------------------

            corrected_df.loc[
                idx,
                'currency'
            ] = target_currency

            corrected_fields[
                'currency'
            ] = target_currency

            # ---------------------------------------------
            # CONVERT JSON LINE ITEM PRICES
            # ---------------------------------------------

            try:

                json_data = json.loads(

                    corrected_df.loc[
                        idx,
                        'line_items_json'
                    ]
                )

                if 'invoice_lines' in json_data:

                    for item in json_data[
                        'invoice_lines'
                    ]:

                        price = item.get(
                            'line',
                            {}
                        ).get(
                            'item_details',
                            {}
                        ).get(
                            'price',
                            0
                        )

                        new_price = round(

                            float(price)
                            * conversion_rate,

                            2
                        )

                        item['line'][
                            'item_details'
                        ]['price'] = new_price

                corrected_df.loc[
                    idx,
                    'line_items_json'
                ] = json.dumps(json_data)

                corrected_fields[
                    'line_items_json'
                ] = 'CURRENCY_CONVERTED'

            except:

                pass

        # =================================================
        # 4. line_item_structure_incompatible
        # =================================================

        if 'line_item_structure_incompatible' in errors:

            try:

                data = json.loads(

                    corrected_df.loc[
                        idx,
                        'line_items_json'
                    ]
                )

                # -----------------------------------------
                # FLAT → NESTED STRUCTURE
                # -----------------------------------------

                if isinstance(data, list):

                    new_structure = {

                        'invoice_lines': []
                    }

                    for i, item in enumerate(data):

                        new_item = {

                            'line': {

                                'id': str(i + 1),

                                'item_details': {

                                    'description':
                                    item.get(
                                        'description',
                                        'UNKNOWN'
                                    ),

                                    'price':
                                    item.get(
                                        'price',
                                        0
                                    ),

                                    'qty':
                                    item.get(
                                        'qty',
                                        1
                                    )
                                }
                            }
                        }

                        new_structure[
                            'invoice_lines'
                        ].append(new_item)

                    corrected_df.loc[
                        idx,
                        'line_items_json'
                    ] = json.dumps(
                        new_structure
                    )

                    corrected_fields[
                        'line_items_json'
                    ] = (
                        'STRUCTURE_CORRECTED'
                    )

            except:

                pass

        # =================================================
        # 5. buyer_vat_missing_for_target
        # =================================================

        if 'buyer_vat_missing_for_target' in errors:

            corrected_df.loc[
                idx,
                'buyer_vat'
            ] = 'MISSING'

            corrected_fields[
                'buyer_vat'
            ] = 'MISSING'

        # =================================================
        # 6. seller_vat_format_invalid
        # =================================================

        if 'seller_vat_format_invalid' in errors:

            corrected_df.loc[
                idx,
                'seller_vat'
            ] = 'INVALID'

            corrected_fields[
                'seller_vat'
            ] = 'INVALID'

        # =================================================
        # 7. credit_note_not_supported
        # =================================================

        if 'credit_note_not_supported' in errors:

            subtotal = corrected_df.loc[
                idx,
                'subtotal'
            ]

            corrected_df.loc[
                idx,
                'subtotal'
            ] = abs(subtotal)

            corrected_fields[
                'subtotal'
            ] = abs(subtotal)

            # ---------------------------------------------
            # RECALCULATE TAX + TOTAL
            # ---------------------------------------------

            tax_rate = corrected_df.loc[
                idx,
                'tax_rate'
            ]

            new_tax = round(
                abs(subtotal) * tax_rate,
                2
            )

            new_total = round(
                abs(subtotal) + new_tax,
                2
            )

            corrected_df.loc[
                idx,
                'tax_amount'
            ] = new_tax

            corrected_df.loc[
                idx,
                'total_amount'
            ] = new_total

            corrected_fields[
                'tax_amount'
            ] = new_tax

            corrected_fields[
                'total_amount'
            ] = new_total

        # =================================================
        # SAVE CORRECTED FIELD CHANGES
        # =================================================

        corrected_fields_list.append(

            json.dumps(corrected_fields)
        )

    # =====================================================
    # ADD corrected_fields COLUMN
    # =====================================================

    corrected_df['corrected_fields'] = (
        corrected_fields_list
    )

    # =====================================================
    # SAVE OUTPUT
    # =====================================================

    corrected_df.to_csv(

        'outputs/corrected_invoice.csv',

        index=False
    )

    print(
        "\nCorrected Invoice Saved Successfully"
    )

    print(
        "\nSaved File : outputs/corrected_invoice.csv"
    )

    return corrected_df