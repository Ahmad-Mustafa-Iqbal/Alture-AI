"""
Alture AI — Hugging Face ZeroGPU Production Entrypoint
=====================================================
Official Hugging Face ZeroGPU implementation using gr.Interface + gr.mount_gradio_app.
"""

import os
import gradio as gr
import spaces
from deployment.backend.main import app as fastapi_app

# 1. Define ZeroGPU inference function
@spaces.GPU
def predict_ats_compatibility(resume_text: str, job_text: str):
    """ZeroGPU inference function for SentenceTransformer + XGBoost matching."""
    from deployment.backend.matcher_service import matcher_service
    match_result = matcher_service.analyze_match(
        resume_text=resume_text or "Sample candidate resume text with Python, FastAPI, ML expertise.",
        jd_text=job_text or "Sample job description seeking AI Engineer with Python, FastAPI, Docker."
    )
    return f"ATS Score: {match_result.ats_score}% | Fit Tier: {match_result.fit_tier}"

# 2. Create Gradio Interface linked to @spaces.GPU function to satisfy ZeroGPU controller
demo = gr.Interface(
    fn=predict_ats_compatibility,
    inputs=[
        gr.Textbox(lines=5, placeholder="Paste candidate resume text here...", label="Candidate Resume"),
        gr.Textbox(lines=5, placeholder="Paste target job description here...", label="Job Description")
    ],
    outputs=gr.Textbox(label="Explainable ATS Result"),
    title="Alture AI — Job Intelligence & ATS Engine",
    description="Multi-Modal NLP & XGBoost ATS Compatibility Engine powered by Hugging Face ZeroGPU."
)

# 3. Mount FastAPI app onto Gradio
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
