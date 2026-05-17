# =========================================================
# predict.py
# Run Model Prediction + Generate Final Output
# =========================================================

import pandas as pd
import joblib

# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load(
    'models/xgboost_multioutput_model.pkl'
)

# =========================================================
# LOAD TARGET COLUMNS
# =========================================================

target_columns = joblib.load(
    'models/target_columns.pkl'
)

# =========================================================
# ERROR COLUMNS
# =========================================================

error_columns = [

    'buyer_vat_missing_for_target',
    'credit_note_not_supported',
    'currency_not_supported',
    'line_item_structure_incompatible',
    'missing_required_field',
    'seller_vat_format_invalid',
    'tax_amount_mismatch'
]

# =========================================================
# MAIN PREDICTION FUNCTION
# =========================================================

def predict_invoice(processed_df, original_invoice_path):

    # -----------------------------------------------------
    # Load Original Invoice
    # -----------------------------------------------------

    original_df = pd.read_csv(
        original_invoice_path
    )

    # =====================================================
    # PREDICT
    # =====================================================

    predictions = model.predict(
        processed_df
    )

    # =====================================================
    # CONVERT TO DATAFRAME
    # =====================================================

    pred_df = pd.DataFrame(

        predictions,

        columns=target_columns
    )

    # =====================================================
    # CREATE FINAL OUTPUT
    # =====================================================

    final_output = pd.DataFrame()

    # -----------------------------------------------------
    # Invoice ID
    # -----------------------------------------------------

    final_output['invoice_id'] = original_df[
        'invoice_id'
    ]

    # -----------------------------------------------------
    # is_mapping_valid
    # -----------------------------------------------------

    final_output['is_mapping_valid'] = pred_df[
        'is_mapping_valid'
    ]

    # =====================================================
    # BUILD mapping_errors COLUMN
    # =====================================================

    mapping_errors = []

    for _, row in pred_df.iterrows():

        current_errors = []

        for error_col in error_columns:

            if row[error_col] == 1:

                current_errors.append(error_col)

        # Convert list -> comma separated string
        error_string = ', '.join(current_errors)

        mapping_errors.append(error_string)

    final_output['mapping_errors'] = mapping_errors

    # =====================================================
    # SAVE OUTPUT
    # =====================================================

    final_output.to_csv(

        'outputs/prediction_output.csv',

        index=False
    )

    print("\nPrediction Output Saved Successfully")

    print(
        "\nSaved File : outputs/prediction_output.csv"
    )

    # =====================================================
    # RETURN OUTPUT
    # =====================================================

    return final_output