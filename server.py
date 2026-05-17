# ==============================================================================
# ROOT ENTRY POINT FOR RENDER DEPLOYMENT
# ==============================================================================
# Render runs `uvicorn server:app` from the root directory by default.
# This file simply forwards the request to the actual backend server.
# ==============================================================================

import os
import sys

# Add the backend folder to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "backend_process_alone"))

# Import the actual FastAPI app
from server import app
