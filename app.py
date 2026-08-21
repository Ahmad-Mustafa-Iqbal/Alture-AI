"""
Alture AI — Hugging Face ZeroGPU Production Entrypoint
=====================================================
Uses user's proven monkeypatching architecture from Ahmad_Mustafa_Iqbal_Portfolio.
"""

import sys
import os
import torch
import spaces
import gradio as gr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 1. Hugging Face ZeroGPU requires at least one function decorated with @spaces.GPU during startup
@spaces.GPU
def dummy_gpu_function():
    return "ZeroGPU is active and working!"

# 2. Import FastAPI app from deployment.backend.main
from deployment.backend.main import app as main_fastapi_app

# 3. Create Gradio Blocks UI (satisfies HF Gradio supervisor & ZeroGPU)
with gr.Blocks(title="Alture AI — Job Intelligence & ATS Engine") as demo:
    gr.Markdown("# Alture AI — Global Job Intelligence & Explainable ATS Engine")
    gr.Markdown("ZeroGPU-Powered Machine Learning Platform for ATS Resume Matching & Live Job Streaming.")
    
    with gr.Row():
        btn = gr.Button("⚡ Test ZeroGPU Status", variant="primary")
        out = gr.Textbox(label="ZeroGPU Status", value="Ready")
    btn.click(fn=dummy_gpu_function, outputs=out)
    
    gr.HTML('''
    <div style="margin-top: 15px; border-top: 2px solid #0284c7; padding-top: 15px;">
        <iframe src="/static/index.html" style="width: 100%; height: 90vh; border: none; border-radius: 8px;"></iframe>
    </div>
    ''')

# 4. Monkeypatch Gradio's internal FastAPI app creator to inject our full backend routes dynamically
original_create_app = gr.routes.App.create_app

def custom_create_app(*args, **kwargs):
    app = original_create_app(*args, **kwargs)
    
    # Configure CORS & Preflight Handling on Gradio's app for Vercel connection
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
            from fastapi.responses import Response
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
    
    # Mount frontend static files
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deployment", "frontend")
    if os.path.exists(frontend_dir):
        app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    # Include all routes from main_fastapi_app
    for route in main_fastapi_app.routes:
        if route not in app.routes:
            app.routes.append(route)
        
    # Reorder routes: move /api and /static routes to the front
    api_routes = []
    other_routes = []
    for route in app.router.routes:
        path = getattr(route, 'path', '')
        if path.startswith("/api") or path.startswith("/static"):
            api_routes.append(route)
        else:
            other_routes.append(route)
            
    app.router.routes = api_routes + other_routes
    return app

# Apply the monkeypatch
gr.routes.App.create_app = custom_create_app

if __name__ == "__main__":
    demo.launch()
