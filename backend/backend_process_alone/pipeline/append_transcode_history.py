import pandas as pd
import json
from sqlalchemy import create_engine
from datetime import datetime

# =====================================================
# DATABASE CONNECTION & INITIALIZATION
# =====================================================

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?sslmode=require"
)

# =====================================================
# DATABASE CONNECTION & INITIALIZATION
# =====================================================

def init_db_and_get_engine():

    try:

        engine = create_engine(DATABASE_URL)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        print("Database connected successfully!")

    except (OperationalError, ProgrammingError) as e:

        print(f"Database connection failed: {e}")

        raise e

    # =================================================
    # CREATE TABLE IF NOT EXISTS
    # =================================================

    try:

        with engine.connect() as conn:

            # Enable extension
            conn.execute(
                text("CREATE EXTENSION IF NOT EXISTS pgcrypto")
            )

            # Create table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS transcode_history (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    invoice_id TEXT,
                    source_format TEXT,
                    target_country TEXT,
                    original_payload JSONB,
                    transcoded_payload JSONB,
                    is_mapping_valid BOOLEAN,
                    mapping_errors TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.commit()

            print("Table verified/created successfully.")

    except Exception as tbl_err:

        print(f"Table creation error: {tbl_err}")

    return engine

# =====================================================
# CLEAN NaN VALUES
# =====================================================

def clean_nan_values(data):

    if isinstance(data, dict):

        return {
            key: clean_nan_values(value)
            for key, value in data.items()
        }

    elif isinstance(data, list):

        return [
            clean_nan_values(item)
            for item in data
        ]

    elif pd.isna(data):

        return None

    else:

        return data

# =====================================================
# FUNCTION
# =====================================================

def append_transcode_history(

    original_csv_path,

    corrected_csv_path,

    prediction_csv_path
):
    engine = init_db_and_get_engine()

    # -------------------------------------------------
    # READ FILES
    # -------------------------------------------------

    original_df = pd.read_csv(original_csv_path)

    corrected_df = pd.read_csv(corrected_csv_path)

    prediction_df = pd.read_csv(prediction_csv_path)

    # -------------------------------------------------
    # CREATE LOOKUP
    # -------------------------------------------------

    prediction_lookup = prediction_df.set_index(
        "invoice_id"
    ).to_dict(orient="index")

    # -------------------------------------------------
    # GET EXISTING IDS
    # -------------------------------------------------

    existing_ids_query = """
    SELECT invoice_id
    FROM transcode_history
    """

    try:
        existing_ids = pd.read_sql(
            existing_ids_query,
            engine
        )["invoice_id"].tolist()
    except Exception as e:
        print(f"Could not read existing transcode history: {e}")
        existing_ids = []

    # -------------------------------------------------
    # FINAL RECORDS
    # -------------------------------------------------

    final_records = []

    # -------------------------------------------------
    # LOOP THROUGH ROWS
    # -------------------------------------------------

    for _, corrected_row in corrected_df.iterrows():

        invoice_id = corrected_row["invoice_id"]

        # ---------------------------------------------
        # SKIP DUPLICATES
        # ---------------------------------------------

        if invoice_id in existing_ids:

            continue

        # ---------------------------------------------
        # ORIGINAL ROW
        # ---------------------------------------------

        original_row = original_df[
            original_df["invoice_id"] == invoice_id
        ]

        if not original_row.empty:

            original_payload = original_row.iloc[0].to_dict()

        else:

            original_payload = {}

        # ---------------------------------------------
        # TRANSCODED PAYLOAD
        # ---------------------------------------------

        transcoded_payload = corrected_row.to_dict()

        # ---------------------------------------------
        # CLEAN NaN VALUES
        # ---------------------------------------------

        original_payload = clean_nan_values(
            original_payload
        )

        transcoded_payload = clean_nan_values(
            transcoded_payload
        )

        # ---------------------------------------------
        # PREDICTION DATA
        # ---------------------------------------------

        prediction_data = prediction_lookup.get(
            invoice_id,
            {}
        )

        is_mapping_valid = bool(
            prediction_data.get(
                "is_mapping_valid",
                0
            )
        )

        mapping_errors = prediction_data.get(
            "mapping_errors",
            ""
        )

        if pd.isna(mapping_errors):

            mapping_errors = ""

        # ---------------------------------------------
        # FINAL RECORD
        # ---------------------------------------------

        final_records.append({

            "invoice_id": invoice_id,

            "source_format": corrected_row[
                "source_format"
            ],

            "target_country": corrected_row[
                "target_country"
            ],

            "original_payload": json.dumps(
                original_payload
            ),

            "transcoded_payload": json.dumps(
                transcoded_payload
            ),

            "is_mapping_valid": is_mapping_valid,

            "mapping_errors": mapping_errors,

            "created_at": datetime.now()
        })

    # -------------------------------------------------
    # DATAFRAME
    # -------------------------------------------------

    final_df = pd.DataFrame(final_records)

    # -------------------------------------------------
    # INSERT INTO POSTGRESQL
    # -------------------------------------------------

    if len(final_df) > 0:

        final_df.to_sql(

            name="transcode_history",

            con=engine,

            if_exists="append",

            index=False
        )

        print(
            "\nTranscode History inserted successfully!"
        )

    else:

        print(
            "\nAll transcode history records already exist."
        )