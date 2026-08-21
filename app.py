"""
Alture AI — Hugging Face ZeroGPU Production Backend Entrypoint
============================================================
FastAPI REST API Server mounted with Gradio ZeroGPU pipeline handler at /gradio.
"""

import os
import uvicorn
import gradio as gr

try:
    import spaces
    @spaces.GPU
    def zero_gpu_pipeline(resume_text: str):
        return "ZeroGPU Pipeline Active & Ready"
except ImportError:
    def zero_gpu_pipeline(resume_text: str):
        return "CPU Pipeline Active & Ready"

from deployment.backend.main import app as fastapi_app

# Create Gradio demo to satisfy ZeroGPU SDK requirement
with gr.Blocks(title="Alture AI Backend API") as demo:
    gr.Markdown("# Alture AI — Production ZeroGPU Backend Engine")
    gr.Markdown("FastAPI REST endpoints available at `/api/v1` for Vercel Frontend integration.")
    btn = gr.Button("⚡ Verify ZeroGPU Pipeline", variant="primary")
    out = gr.Textbox(label="Pipeline Output")
    btn.click(zero_gpu_pipeline, inputs=gr.Textbox(value="Sample Resume"), outputs=out)

# Mount Gradio onto FastAPI app at /gradio so root FastAPI routes remain 100% clean
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 Launching Alture AI ZeroGPU Engine on Port {port}...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
