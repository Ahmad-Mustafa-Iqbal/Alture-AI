import os
import sys
import torch
import gradio as gr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

try:
    import spaces
    @spaces.GPU
    def dummy_gpu_function():
        return "ZeroGPU ready"
except ImportError:
    def dummy_gpu_function():
        return "CPU mode"

from deployment.backend.main import app as main_fastapi_app

with gr.Blocks(title="Alture AI Backend API") as demo:
    gr.Markdown("# Alture AI — ZeroGPU Backend Engine")
    gr.Markdown("REST API available under `/api/v1` and `/v1`.")
    btn = gr.Button("Verify ZeroGPU Pipeline", variant="primary")
    out = gr.Textbox(label="Pipeline Output")
    btn.click(dummy_gpu_function, outputs=out)

# Mount FastAPI app onto Gradio routes
original_create_app = gr.routes.App.create_app

def custom_create_app(*args, **kwargs):
    app = original_create_app(*args, **kwargs)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(main_fastapi_app.router)
    
    # Ensure API routes take precedence over Gradio static handlers
    api_routes = []
    other_routes = []
    for route in app.router.routes:
        path = getattr(route, 'path', '')
        if path.startswith("/api") or path.startswith("/v1") or path.startswith("/health"):
            api_routes.append(route)
        else:
            other_routes.append(route)
            
    app.router.routes = api_routes + other_routes
    return app

gr.routes.App.create_app = custom_create_app

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
