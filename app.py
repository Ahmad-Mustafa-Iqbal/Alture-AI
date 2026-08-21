"""
Alture AI — Hugging Face Space Entrypoint
=========================================
Launches the FastAPI backend and mounted React frontend on Hugging Face Spaces (Port 7860).
"""

import os
import uvicorn
import gradio as gr
from deployment.backend.main import app as fastapi_app

# Mount Gradio into FastAPI for Hugging Face Spaces SDK compatibility
demo = gr.Blocks(title="Alture AI — Job Intelligence & ATS Engine")

# Mount Gradio into FastAPI so both the React UI at / and Gradio are active
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 Launching Alture AI on Hugging Face Space (Port {port})...")
    uvicorn.run(app, host="0.0.0.0", port=port)
