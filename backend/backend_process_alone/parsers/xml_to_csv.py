# =========================================================
# xml_to_csv.py
# Convert XML Invoice -> CSV
# =========================================================

import xmltodict
import pandas as pd
import json
import os

def convert_xml_to_csv(xml_path):

    # -----------------------------------------------------
    # Read XML
    # -----------------------------------------------------

    with open(xml_path, 'r', encoding='utf-8') as file:

        xml_data = file.read()

    # -----------------------------------------------------
    # Parse XML
    # -----------------------------------------------------

    data_dict = xmltodict.parse(xml_data)

    # -----------------------------------------------------
    # Flatten XML Structure
    # -----------------------------------------------------

    df = pd.json_normalize(data_dict)

    # -----------------------------------------------------
    # Create Output Path
    # -----------------------------------------------------

    file_name = os.path.basename(xml_path).split('.')[0]

    output_path = f'converted/{file_name}.csv'

    # -----------------------------------------------------
    # Save CSV
    # -----------------------------------------------------

    df.to_csv(output_path, index=False)

    return output_path