# =========================================================
# preprocess.py
# Convert Invoice -> Model Ready X
# Format Rules Loaded Internally
# =========================================================

import pandas as pd
import json
import joblib

# =========================================================
# LOAD TRAINED ARTIFACTS
# =========================================================

feature_columns = joblib.load(
    'models/feature_columns.pkl'
)

encoders = joblib.load(
    'models/label_encoders.pkl'
)

# =========================================================
# LOAD FORMAT RULES
# =========================================================

format_df = pd.read_csv(
    r'data\format_rules.csv'
)

# =========================================================
# MAIN PREPROCESS FUNCTION
# =========================================================

def preprocess_invoice(invoice_csv_path):

    # =====================================================
    # LOAD INVOICE FILE
    # =====================================================

    invoice_df = pd.read_csv(invoice_csv_path)

    # =====================================================
    # MAP TARGET COUNTRY -> TARGET FORMAT
    # =====================================================

    def find_target_format(country):

        country = str(country).lower()

        for _, row in format_df.iterrows():

            countries = str(
                row['used_in_countries']
            ).lower()

            if country in countries:

                return row['format_id']

        return 'unknown'

    invoice_df['target_format'] = invoice_df[
        'target_country'
    ].apply(find_target_format)

    # =====================================================
    # MERGE FORMAT RULES
    # =====================================================

    df = invoice_df.merge(

        format_df,

        left_on='target_format',
        right_on='format_id',

        how='left'
    )

    # =====================================================
    # FEATURE ENGINEERING
    # =====================================================

    # -----------------------------------------------------
    # Tax Features
    # -----------------------------------------------------

    df['expected_tax'] = (
        df['subtotal'] * df['tax_rate']
    ).round(2)

    df['tax_difference'] = abs(

        df['tax_amount'] - df['expected_tax']

    ).round(2)

    # -----------------------------------------------------
    # Currency Supported
    # -----------------------------------------------------

    def currency_check(row):

        try:

            supported = str(
                row['supported_currencies']
            )

            return (
                1
                if row['currency'] in supported
                else 0
            )

        except:

            return 0

    df['currency_supported'] = df.apply(
        currency_check,
        axis=1
    )

    # =====================================================
    # JSON FEATURE EXTRACTION
    # =====================================================

    def get_line_item_count(x):
        try:
            data = json.loads(x)
            if 'invoice_lines' in data:
                return len(data['invoice_lines'])
            return 0
        except:
            return 0

    def get_total_quantity(x):
        try:
            data = json.loads(x)

            total_qty = 0

            if 'invoice_lines' in data:

                for item in data['invoice_lines']:

                    qty = item.get('line', {}) \
                              .get('item_details', {}) \
                              .get('qty', 0)

                    total_qty += qty

            return total_qty

        except:

            return 0

    def get_avg_price(x):

        try:

            data = json.loads(x)

            prices = []

            if 'invoice_lines' in data:

                for item in data['invoice_lines']:

                    price = item.get('line', {}) \
                                .get('item_details', {}) \
                                .get('price', 0)

                    prices.append(price)

            if len(prices) == 0:

                return 0

            return sum(prices) / len(prices)

        except:

            return 0

    def has_negative_price(x):

        try:

            data = json.loads(x)

            if 'invoice_lines' in data:

                for item in data['invoice_lines']:

                    price = item.get('line', {}) \
                                .get('item_details', {}) \
                                .get('price', 0)

                    if price < 0:

                        return 1

            return 0

        except:

            return 0

    # -----------------------------------------------------
    # Apply JSON Features
    # -----------------------------------------------------

    df['line_item_count'] = df[
        'line_items_json'
    ].apply(get_line_item_count)

    df['total_quantity'] = df[
        'line_items_json'
    ].apply(get_total_quantity)

    df['avg_item_price'] = df[
        'line_items_json'
    ].apply(get_avg_price)

    df['has_negative_price'] = df[
        'line_items_json'
    ].apply(has_negative_price)

    # =====================================================
    # MISSING VALUE FEATURES
    # =====================================================

    df['seller_vat_missing'] = (
        df['seller_vat'].isnull().astype(int)
    )

    df['buyer_vat_missing'] = (
        df['buyer_vat'].isnull().astype(int)
    )

    df['payment_reference_missing'] = (
        df['payment_reference'].isnull().astype(int)
    )

    df['delivery_date_missing'] = (
        df['delivery_date'].isnull().astype(int)
    )

    # =====================================================
    # REQUIRED FIELD CHECK
    # =====================================================

    def count_missing_required(row):

        try:

            required = str(
                row['required_fields']
            ).split(',')

            missing = 0

            for field in required:

                field = field.strip()

                if field in row.index:

                    value = row[field]

                    if pd.isnull(value):

                        missing += 1

            return missing

        except:

            return 0

    df['missing_required_count'] = df.apply(
        count_missing_required,
        axis=1
    )

    # =====================================================
    # KEEP ONLY MODEL FEATURES
    # =====================================================

    df = df[feature_columns]

    # =====================================================
    # HANDLE NULL VALUES
    # =====================================================

    df = df.fillna('missing')

    # =====================================================
    # ENCODE CATEGORICAL FEATURES
    # =====================================================

    categorical_cols = df.select_dtypes(
        include='object'
    ).columns

    for col in categorical_cols:

        if col in encoders:

            le = encoders[col]

            df[col] = df[col].astype(str)

            known_values = set(le.classes_)

            df[col] = df[col].apply(

                lambda x:
                x if x in known_values
                else le.classes_[0]
            )

            df[col] = le.transform(df[col])

    # =====================================================
    # SAVE PROCESSED OUTPUT
    # =====================================================

    df.to_csv(

        'processed/processed_invoice.csv',

        index=False
    )

    return df