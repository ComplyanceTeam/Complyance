import os
import sys

# =========================================================
# Path Setup - Delegate to backend_process_alone/server.py
# =========================================================
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PIPELINE_DIR = os.path.join(_BACKEND_DIR, "backend_process_alone")

# Insert the inner folder at the beginning of sys.path
if _PIPELINE_DIR not in sys.path:
    sys.path.insert(0, _PIPELINE_DIR)

# Temporarily remove the outer backend folder from sys.path
# to avoid Python finding the outer server.py and crashing with circular imports.
original_sys_path = list(sys.path)
try:
    while _BACKEND_DIR in sys.path:
        sys.path.remove(_BACKEND_DIR)
    while "" in sys.path:
        sys.path.remove("")
        
    # Import the FastAPI app instance from inner server.py
    from server import app
finally:
    sys.path = original_sys_path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
