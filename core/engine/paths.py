import os

# Base directory of the 'core' package
CORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_data_path(filename):
    return os.path.join(CORE_DIR, "data", filename)

def get_model_path(filename):
    return os.path.join(CORE_DIR, "models", filename)
