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
    # DEBUG ROOT TAGS
    # -----------------------------------------------------

    print("\nDetected XML Root Tags:")
    print(data_dict.keys())

    # -----------------------------------------------------
    # GET ROOT KEY
    # -----------------------------------------------------

    root_key = list(
        data_dict.keys()
    )[0]

    root_data = data_dict[
        root_key
    ]

    # -----------------------------------------------------
    # DETECT INVOICE DATA
    # -----------------------------------------------------

    invoices = None

    # Case 1
    # <Invoices><Invoice>...</Invoice></Invoices>

    if isinstance(root_data, dict):

        if 'Invoice' in root_data:

            invoices = root_data[
                'Invoice'
            ]

        elif 'invoice' in root_data:

            invoices = root_data[
                'invoice'
            ]

        else:

            invoices = root_data

    # Case 2
    # Direct list

    elif isinstance(root_data, list):

        invoices = root_data

    # -----------------------------------------------------
    # SINGLE INVOICE FIX
    # -----------------------------------------------------

    if isinstance(invoices, dict):

        invoices = [invoices]

    # -----------------------------------------------------
    # SAFETY CHECK
    # -----------------------------------------------------

    if invoices is None:

        print(
            "\nCould Not Detect Invoice Structure"
        )

        return None

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
    # NORMALIZE COLUMN NAMES
    # -----------------------------------------------------

    df.columns = (

        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
    )

    # -----------------------------------------------------
    # RENAME POSSIBLE INVOICE ID COLUMNS
    # -----------------------------------------------------

    possible_invoice_cols = [

        'invoiceid',
        'invoice_id',
        'invoice_number',
        'invoicenumber'
    ]

    for col in possible_invoice_cols:

        if col in df.columns:

            df.rename(

                columns={
                    col: 'invoice_id'
                },

                inplace=True
            )

            break

    # -----------------------------------------------------
    # DEBUG PRINT COLUMNS
    # -----------------------------------------------------

    print("\nDetected Columns:")
    print(df.columns.tolist())

    # -----------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # -----------------------------------------------------

    os.makedirs(

        'processed/converted',

        exist_ok=True
    )

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