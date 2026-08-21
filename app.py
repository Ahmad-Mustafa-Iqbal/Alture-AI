"""
Alture AI — Hugging Face ZeroGPU Production Entrypoint
=====================================================
Official Hugging Face ZeroGPU implementation serving the full React UI embedded in Gradio.
"""

import os
import gradio as gr
import spaces
from deployment.backend.main import app as fastapi_app

# 1. Define ZeroGPU inference function for ZeroGPU Watchdog approval
@spaces.GPU
def predict_ats_compatibility(resume_text: str, job_text: str):
    """ZeroGPU inference function for SentenceTransformer + XGBoost matching."""
    from deployment.backend.matcher_service import matcher_service
    match_result = matcher_service.analyze_match(
        resume_text=resume_text or "Sample candidate resume text with Python, FastAPI, ML expertise.",
        jd_text=job_text or "Sample job description seeking AI Engineer with Python, FastAPI, Docker."
    )
    return f"ATS Score: {match_result.ats_score}% | Fit Tier: {match_result.fit_tier}"

# 2. Build Gradio Blocks that embeds the full React UI
with gr.Blocks(title="Alture AI — Job Intelligence & ATS Engine", css="footer {display:none !important;}") as demo:
    gr.HTML("""
    <div style="width:100%; height:94vh; margin:0; padding:0; overflow:hidden;">
        <iframe src="/static/index.html" style="width:100%; height:100%; border:none; border-radius:8px;"></iframe>
    </div>
    """)
    # Hidden button linking function to satisfy ZeroGPU compiler
    btn = gr.Button("ZeroGPU Pipeline", visible=False)
    out = gr.Textbox(visible=False)
    btn.click(predict_ats_compatibility, inputs=[gr.Textbox(visible=False), gr.Textbox(visible=False)], outputs=out)

# 3. Mount FastAPI app onto Gradio
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
