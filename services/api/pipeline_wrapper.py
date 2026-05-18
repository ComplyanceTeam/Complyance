import os
import sys
import json
import pandas as pd
import uuid
import shutil
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

# Base directory for API
BASE_DIR = os.path.dirname(__file__)

def run_transcode_pipeline(input_data: Any, file_type: str = "json") -> Dict[str, Any]:
    """
    Orchestrates the transcoding pipeline for a single invoice.
    Accepts a dict for JSON input or raw file content for CSV/XML.
    Thread-safe version: uses unique directories per request and isolated execution.
    """
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(BASE_DIR, f"run_{session_id}")
    
    # Setup isolated structure
    temp_dir = os.path.join(session_dir, "temp")
    outputs_dir = os.path.join(session_dir, "outputs")
    processed_dir = os.path.join(session_dir, "processed")
    
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(os.path.join(processed_dir, "converted"), exist_ok=True)
    
    # Save input data
    temp_input_path = os.path.join(temp_dir, f"input_invoice.{file_type}")
    with open(temp_input_path, "w", encoding="utf-8") as f:
        if file_type == "json":
            json.dump([input_data], f)
        else:
            if isinstance(input_data, (bytes, bytearray)):
                f.write(input_data.decode("utf-8"))
            else:
                f.write(str(input_data))
        
    original_cwd = os.getcwd()
    
    try:
        # Move to session directory to isolate hardcoded file operations
        os.chdir(session_dir)
        
        # 1. Parse
        if file_type == 'json':
            csv_path = convert_json_to_csv(temp_input_path)
        elif file_type == 'xml':
            csv_path = convert_xml_to_csv(temp_input_path)
        else:
            csv_path = load_csv(temp_input_path)

        if not csv_path:
            raise ValueError("Failed to convert input to CSV for processing.")
            
        # 2. Preprocess
        processed_df = preprocess_invoice(csv_path)
        
        # 3. Predict
        predict_invoice(processed_df, csv_path)
        
        # 4. Correct
        correct_invoice(csv_path, 'outputs/prediction_output.csv')
        
        # 5. Transcode
        map_invoice('outputs/corrected_invoice.csv', file_type)
        
        # 6. Collect Results
        pred_df = pd.read_csv('outputs/prediction_output.csv')
        is_mapping_valid = bool(pred_df.iloc[0]['is_mapping_valid'])
        mapping_errors = str(pred_df.iloc[0]['mapping_errors']) if not pd.isna(pred_df.iloc[0]['mapping_errors']) else ""

        invoice_snapshot = {}
        try:
            snapshot_df = pd.read_csv(csv_path)
            if not snapshot_df.empty:
                invoice_snapshot = snapshot_df.iloc[0].to_dict()
        except Exception:
            if isinstance(input_data, dict):
                invoice_snapshot = dict(input_data)

        if invoice_snapshot:
            try:
                invoice_snapshot = json.loads(json.dumps(invoice_snapshot, default=str))
            except Exception:
                pass
        
        # Get target_format from corrected invoice (after resolution)
        corr_df = pd.read_csv('outputs/corrected_invoice.csv')
        # We need the format name, not ID. Correction/Mapper uses country to resolve it again.
        # But wait, we can just use the name from transcoded_payload if we want.
        
        final_mapped_path = 'outputs/final_mapped_invoice.csv'
        if file_type == 'json':
            final_mapped_path = 'outputs/final_mapped_invoice.json'
            with open(final_mapped_path, 'r', encoding='utf-8') as f:
                transcoded_payload = json.load(f)[0]
        else:
            mapped_df = pd.read_csv(final_mapped_path)
            transcoded_payload = mapped_df.iloc[0].to_dict()
            
        invoice_id = invoice_snapshot.get("invoice_id", "UNKNOWN") if isinstance(invoice_snapshot, dict) else "UNKNOWN"
        source_format = invoice_snapshot.get("source_format", "UNKNOWN") if isinstance(invoice_snapshot, dict) else "UNKNOWN"
        original_payload = input_data if isinstance(input_data, dict) else invoice_snapshot or {"file_type": file_type}

        return clean_nan_values({
            "invoice_id": invoice_id,
            "source_format": source_format,
            "target_format": str(transcoded_payload.get("_syntax", "UNKNOWN")),
            "original_payload": original_payload,
            "transcoded_payload": transcoded_payload,
            "is_mapping_valid": is_mapping_valid,
            "mapping_errors": mapping_errors
        })
        
    except Exception as e:
        print(f"Pipeline error for session {session_id}: {str(e)}")
        raise e
    finally:
        os.chdir(original_cwd)
        # Cleanup
        shutil.rmtree(session_dir, ignore_errors=True)
