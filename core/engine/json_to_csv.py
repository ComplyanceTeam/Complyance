# =========================================================
# json_to_csv.py
# Convert JSON Invoice -> CSV
# =========================================================

import pandas as pd
import json
import os

def convert_json_to_csv(json_path):

    # -----------------------------------------------------
    # Read JSON
    # -----------------------------------------------------

    with open(json_path, 'r', encoding='utf-8') as file:

        data = json.load(file)

    # -----------------------------------------------------
    # Flatten JSON
    # -----------------------------------------------------

    df = pd.json_normalize(data)

    # -----------------------------------------------------
    # Create Output Path
    # -----------------------------------------------------

    file_name = os.path.basename(json_path).split('.')[0]

    output_path = f'processed/converted/{file_name}.csv'

    # -----------------------------------------------------
    # Save CSV
    # -----------------------------------------------------

    df.to_csv(output_path, index=False)

    return output_path