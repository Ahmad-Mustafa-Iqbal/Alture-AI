"""
Alture AI — Hugging Face ZeroGPU Production Backend Entrypoint
============================================================
Official Hugging Face ZeroGPU production runner using user's proven monkeypatching pattern.
"""

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
        return "ZeroGPU is active and ready"
except ImportError:
    def dummy_gpu_function():
        return "Local CPU mode"

from deployment.backend.main import app as main_fastapi_app

# Create Gradio demo to satisfy ZeroGPU compiler
with gr.Blocks(title="Alture AI Backend API") as demo:
    gr.Markdown("# Alture AI — Production ZeroGPU Backend Engine")
    gr.Markdown("FastAPI REST endpoints available under `/api/v1` and `/v1`.")
    btn = gr.Button("⚡ Verify ZeroGPU Pipeline", variant="primary")
    out = gr.Textbox(label="Pipeline Output")
    btn.click(dummy_gpu_function, outputs=out)

# Monkeypatch Gradio's internal FastAPI app creator (proven portfolio pattern)
original_create_app = gr.routes.App.create_app

def custom_create_app(*args, **kwargs):
    app = original_create_app(*args, **kwargs)
    
    # Configure CORS & preflight middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def cors_preflight_middleware(request, call_next):
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    # Inject main FastAPI app router
    app.include_router(main_fastapi_app.router)
    
    # Reorder routes so /api and /v1 routes take precedence
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
