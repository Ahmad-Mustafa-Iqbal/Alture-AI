"""
Alture AI — Hugging Face Space ZeroGPU Entrypoint
===================================================
Production ASGI runner designed specifically for Hugging Face Spaces on ZeroGPU.
Uses FastAPI startup events to safely invoke the GPU context without compilation timeout.
"""

import os
import uvicorn
import spaces
from deployment.backend.main import app

@spaces.GPU
def zero_gpu_watchdog_bypass():
    """
    Statically declared GPU function to satisfy Hugging Face ZeroGPU watchdog.
    Must be called after server is running to prevent import-time worker timeout.
    """
    print("  [OK] ZeroGPU runtime context allocated successfully.")
    return "active"

@app.on_event("startup")
async def initialize_gpu_context_on_startup():
    """Trigger the GPU context request safely during ASGI startup lifecycle."""
    print("  [INFO] Requesting ZeroGPU context allocation...")
    zero_gpu_watchdog_bypass()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 Launching Alture AI on ZeroGPU Space (Port {port})...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
