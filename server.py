# ==============================================================================
# ROOT ENTRY POINT FOR RENDER DEPLOYMENT
# ==============================================================================
# Render runs `uvicorn server:app` from the root directory by default.
# This file simply forwards the request to the actual backend server.
# ==============================================================================

import os
import sys

# Add the root directory to path so the backend package can be found
sys.path.insert(0, os.path.dirname(__file__))

# Import using absolute package path to avoid circular imports 
# (since this file is also named server.py)
from backend.backend_process_alone.server import app
