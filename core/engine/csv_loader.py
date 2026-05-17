# =========================================================
# csv_loader.py
# Load Existing CSV
# =========================================================

import pandas as pd

def load_csv(csv_path):

    # Simple validation load

    df = pd.read_csv(csv_path)

    # Return same path
    return csv_path