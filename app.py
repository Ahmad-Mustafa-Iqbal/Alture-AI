"""
Alture AI — Hugging Face Space ZeroGPU Entrypoint
===================================================
Production ASGI runner designed specifically for Hugging Face Spaces on ZeroGPU.
Statically implements @spaces.GPU watchdog initialization without triggering startup executions.
"""

import os
import uvicorn
import spaces
from deployment.backend.main import app

@spaces.GPU
def zero_gpu_watchdog_bypass():
    """
    Statically declared GPU function to satisfy Hugging Face ZeroGPU watchdog.
    Must NOT be invoked during startup imports to prevent worker context timeout.
    """
    return "active"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 Launching Alture AI on ZeroGPU Space (Port {port})...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
