"""
Alture AI — Hugging Face Space Entrypoint
=========================================
Launches the FastAPI backend and mounted React frontend on Hugging Face Spaces (Port 7860).
"""

import os
import uvicorn
from deployment.backend.main import app

if __name__ == "__main__":
    # Hugging Face Spaces default port is 7860
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 Launching Alture AI on Hugging Face Space (Port {port})...")
    uvicorn.run(app, host="0.0.0.0", port=port)
