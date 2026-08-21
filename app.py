"""
Alture AI — Hugging Face Space Production Entrypoint
===================================================
Directly runs the FastAPI application and React web frontend on Port 7860.
No conflicting Gradio dependencies needed!
"""

import os
import uvicorn
from deployment.backend.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 Launching Alture AI Production Engine on Hugging Face Spaces (Port {port})...")
    uvicorn.run(app, host="0.0.0.0", port=port)
