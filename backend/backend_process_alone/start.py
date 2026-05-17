# =========================================================
# start.py
# Main Entry Point
# =========================================================

import os

# ---------------------------------------------------------
# Parser Imports
# ---------------------------------------------------------

from parsers.xml_to_csv import convert_xml_to_csv
from parsers.json_to_csv import convert_json_to_csv
from parsers.csv_loader import load_csv
from pipeline.append_transcode_history import append_transcode_history
# ---------------------------------------------------------
# Pipeline Imports
# ---------------------------------------------------------

from pipeline.preprocess import preprocess_invoice

from pipeline.predict import predict_invoice

from pipeline.correction import correct_invoice

from pipeline.mapper import map_invoice

# =========================================================
# INPUT FILE
# =========================================================

file_path = input(
    "Enter invoice file path: "
)

# =========================================================
# CHECK FILE EXISTS
# =========================================================

if not os.path.exists(file_path):

    print("File does not exist.")

    exit()

# =========================================================
# DETECT FILE TYPE
# =========================================================

file_extension = file_path.split('.')[-1].lower()

print(
    f"\nDetected File Type : {file_extension}"
)

# =========================================================
# PARSE FILE
# =========================================================

if file_extension == 'xml':

    print("\nConverting XML to CSV...")

    csv_path = convert_xml_to_csv(
        file_path
    )

elif file_extension == 'json':

    print("\nConverting JSON to CSV...")

    csv_path = convert_json_to_csv(
        file_path
    )

elif file_extension == 'csv':

    print("\nLoading CSV file...")

    csv_path = load_csv(
        file_path
    )

else:

    print("Unsupported file type.")

    exit()

print(f"\nCSV Ready : {csv_path}")

# =========================================================
# PREPROCESSING
# =========================================================

print(
    "\nStarting preprocessing pipeline..."
)

processed_df = preprocess_invoice(
    csv_path
)

print(
    "\nPreprocessing completed."
)

# =========================================================
# PREDICTION
# =========================================================

print(
    "\nRunning model prediction..."
)

prediction_output = predict_invoice(

    processed_df,

    csv_path
)

print(
    "\nPrediction completed."
)

# =========================================================
# SHOW PREDICTION PREVIEW
# =========================================================

print(
    "\nPrediction Output Preview:\n"
)

print(
    prediction_output.head()
)

# =========================================================
# CORRECTION ENGINE
# =========================================================

print(
    "\nStarting correction engine..."
)

corrected_df = correct_invoice(

    csv_path,

    'outputs/prediction_output.csv'
)

print(
    "\nCorrection completed."
)

# =========================================================
# TARGET FORMAT TRANSCODING
# =========================================================

print(
    "\nStarting invoice transcoding..."
)

mapped_df = map_invoice(

    'outputs/corrected_invoice.csv',

    file_extension
)

print(
    "\nTranscoding completed."
)

# =========================================================
# FINAL OUTPUT SUMMARY
# =========================================================

print("\nGenerated Files:\n")

# ---------------------------------------------------------
# Always Generated
# ---------------------------------------------------------

print(
    "1. outputs/prediction_output.csv"
)

print(
    "2. outputs/corrected_invoice.csv"
)

print(
    "3. outputs/final_mapped_invoice.csv"
)

# ---------------------------------------------------------
# JSON Input Extra Output
# ---------------------------------------------------------

if file_extension == 'json':

    print(
        "4. outputs/final_mapped_invoice.json"
    )

# ---------------------------------------------------------
# XML Input Extra Output
# ---------------------------------------------------------

elif file_extension == 'xml':

    print(
        "4. outputs/final_mapped_invoice.xml"
    )

# =========================================================
# APPEND TRANSCODE HISTORY
# =========================================================

print(
    "\nAppending transcode history into PostgreSQL..."
)

append_transcode_history(

    file_path,

    'outputs/corrected_invoice.csv',

    'outputs/prediction_output.csv'
)

print(
    "\nTranscode history append completed."
)
# =========================================================
# FINAL MESSAGE
# =========================================================

print(
    "\nPipeline Completed Successfully."
)