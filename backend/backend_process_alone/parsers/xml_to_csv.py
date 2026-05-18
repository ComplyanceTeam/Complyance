# =========================================================
# xml_to_csv.py
# Convert XML Invoice -> CSV
# =========================================================

import xmltodict
import pandas as pd
import os

# =========================================================
# MAIN FUNCTION
# =========================================================

def convert_xml_to_csv(xml_path):

    # -----------------------------------------------------
    # READ XML
    # -----------------------------------------------------

    with open(

        xml_path,

        'r',

        encoding='utf-8'

    ) as file:

        xml_data = file.read()

    # -----------------------------------------------------
    # PARSE XML
    # -----------------------------------------------------

    data_dict = xmltodict.parse(
        xml_data
    )

    # -----------------------------------------------------
    # EXTRACT INVOICE LIST
    # -----------------------------------------------------

    invoices = data_dict[
        'Invoices'
    ][
        'Invoice'
    ]

    # -----------------------------------------------------
    # SINGLE INVOICE FIX
    # -----------------------------------------------------

    if isinstance(invoices, dict):

        invoices = [invoices]

    # -----------------------------------------------------
    # CREATE DATAFRAME
    # -----------------------------------------------------

    df = pd.DataFrame(
        invoices
    )

    # -----------------------------------------------------
    # PRESERVE RAW VALUES
    # -----------------------------------------------------

    df = df.fillna('')

    # -----------------------------------------------------
    # CREATE OUTPUT PATH
    # -----------------------------------------------------

    file_name = os.path.basename(
        xml_path
    ).split('.')[0]

    output_path = (

        f'processed/converted/'
        f'{file_name}.csv'
    )

    # -----------------------------------------------------
    # SAVE CSV
    # -----------------------------------------------------

    df.to_csv(

        output_path,

        index=False
    )

    print(
        "\nXML Successfully Converted To CSV"
    )

    print(
        f"\nSaved File : {output_path}"
    )

    # -----------------------------------------------------
    # RETURN CSV PATH
    # -----------------------------------------------------

    return output_path