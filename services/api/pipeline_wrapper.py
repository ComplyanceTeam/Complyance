import os
import sys
import json
import pandas as pd
from typing import Dict, Any

# Add the root directory to sys.path so we can import 'core'
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.engine.xml_to_csv import convert_xml_to_csv
from core.engine.json_to_csv import convert_json_to_csv
from core.engine.csv_loader import load_csv
from core.engine.preprocess import preprocess_invoice
from core.engine.predict import predict_invoice
from core.engine.correction import correct_invoice
from core.engine.mapper import map_invoice
from core.engine.utils import clean_nan_values

# Base directory for outputs (relative to this file for container safety)
BASE_DIR = os.path.dirname(__file__)
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def run_transcode_pipeline(input_data: Dict[Any, Any], file_type: str = "json") -> Dict[str, Any]:
    """
    Orchestrates the transcoding pipeline for a single invoice provided as a dictionary.
    """
    # Create temporary directory for API processing
    temp_dir = os.path.join(BASE_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save input data to a temporary file
    temp_input_path = os.path.join(temp_dir, f"input_invoice.{file_type}")
    with open(temp_input_path, "w", encoding="utf-8") as f:
        if file_type == "json":
            json.dump([input_data], f)
        
    # We need to manage the working directory for 'outputs' and 'processed' to be found by the engine
    # The current engine expects these folders in the CWD
    original_cwd = os.getcwd()
    os.chdir(BASE_DIR)
    
    try:
        # 1. Parse
        if file_type == 'json':
            csv_path = convert_json_to_csv(temp_input_path)
        else:
            csv_path = load_csv(temp_input_path)
            
        # 2. Preprocess
        processed_df = preprocess_invoice(csv_path)
        
        # 3. Predict
        predict_invoice(processed_df, csv_path)
        
        # 4. Correct
        correct_invoice(csv_path, 'outputs/prediction_output.csv')
        
        # 5. Transcode
        map_invoice('outputs/corrected_invoice.csv', file_type)
        
        # 6. Collect Results
        # Read prediction output
        pred_df = pd.read_csv('outputs/prediction_output.csv')
        is_mapping_valid = bool(pred_df.iloc[0]['is_mapping_valid'])
        mapping_errors = str(pred_df.iloc[0]['mapping_errors']) if not pd.isna(pred_df.iloc[0]['mapping_errors']) else ""
        
        # Read final mapped result
        final_mapped_path = 'outputs/final_mapped_invoice.csv'
        if file_type == 'json':
            final_mapped_path = 'outputs/final_mapped_invoice.json'
            with open(final_mapped_path, 'r', encoding='utf-8') as f:
                transcoded_payload = json.load(f)[0]
        else:
            mapped_df = pd.read_csv(final_mapped_path)
            transcoded_payload = mapped_df.iloc[0].to_dict()
            
        return clean_nan_values({
            "invoice_id": input_data.get("invoice_id", "UNKNOWN"),
            "source_format": input_data.get("source_format", "UNKNOWN"),
            "target_format": transcoded_payload.get("target_format", "UNKNOWN"),
            "original_payload": input_data,
            "transcoded_payload": transcoded_payload,
            "is_mapping_valid": is_mapping_valid,
            "mapping_errors": mapping_errors
        })
        
    except Exception as e:
        print(f"Pipeline error: {str(e)}")
        raise e
    finally:
        os.chdir(original_cwd)
