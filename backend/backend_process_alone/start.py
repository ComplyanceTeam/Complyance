import os

from parsers.xml_to_csv import convert_xml_to_csv
from parsers.json_to_csv import convert_json_to_csv
from parsers.csv_loader import load_csv
from pipeline.preprocess import preprocess_invoice
from pipeline.predict import predict_invoice
from pipeline.correction import correct_invoice
from pipeline.mapper import map_invoice

file_path = input(
    "Enter invoice file path: "
)

if not os.path.exists(file_path):
    print("File does not exist.")
    exit()

file_extension = file_path.split('.')[-1].lower()

print(
    f"\nDetected File Type : {file_extension}"
)

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

print(
    "\nStarting preprocessing pipeline..."
)
processed_df = preprocess_invoice(
    csv_path
)
print(
    "\nPreprocessing completed."
)

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

print(
    "\nPrediction Output Preview:\n"
)
print(
    prediction_output.head()
)

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

print(
    "\nStarting invoice transcoding..."

mapped_df = map_invoice(
    'outputs/corrected_invoice.csv',
    file_extension
)
print(
    "\nTranscoding completed."
)

print("\nGenerated Files:\n")

print(
    "1. outputs/prediction_output.csv"
)
print(
    "2. outputs/corrected_invoice.csv"
)
print(
    "3. outputs/final_mapped_invoice.csv"
)

if file_extension == 'json':
    print(
        "4. outputs/final_mapped_invoice.json"
    )

elif file_extension == 'xml':
    print(
        "4. outputs/final_mapped_invoice.xml"
    )

print(
    "\nPipeline Completed Successfully."
)