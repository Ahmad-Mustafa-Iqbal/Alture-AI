"""
Alture AI — Hugging Face Space Production Backend Entrypoint
============================================================
Pure FastAPI ASGI runner for Hugging Face Spaces (Port 7860).
Serves all REST APIs directly with CORS enabled for Vercel Frontend.
"""

import os
import uvicorn
from deployment.backend.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 Launching Alture AI Backend Engine on Port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
