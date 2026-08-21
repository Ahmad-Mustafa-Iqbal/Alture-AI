import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .schemas import (
    SingleMatchRequest, SingleMatchResponse,
    BatchMatchRequest, BatchMatchResponse,
    SampleDataResponse
)
from .matcher_service import matcher_service
from .sample_data import SAMPLE_PERSONAS, SAMPLE_JOBS

app = FastAPI(
    title="Alture AI — Global Job Intelligence & Explainable ATS Engine",
    description="Production REST API powering hybrid semantic matching, 500+ skill ontology extraction, and ATS compatibility scoring.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local development and microservices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# API ROUTERS
# ----------------------------------------------------
@app.get("/health", tags=["Health & System"])
async def health_check():
    """Health check endpoint to verify backend operational readiness."""
    return {
        "status": "healthy",
        "service": "Alture AI Matcher Engine",
        "version": "2.0.0",
        "sbert_loaded": matcher_service.sbert_model is not None,
        "models_loaded": matcher_service.xgb_model is not None or matcher_service.lgb_model is not None
    }

@app.get("/api/v1/sample-data", response_model=SampleDataResponse, tags=["Sample Data"])
async def get_sample_data():
    """Retrieve preloaded test candidate personas and global job postings."""
    return SampleDataResponse(
        personas=SAMPLE_PERSONAS,
        jobs=SAMPLE_JOBS
    )

@app.post("/api/v1/analyze", response_model=SingleMatchResponse, tags=["ATS Matching"])
async def analyze_single_match(request: SingleMatchRequest):
    """
    Perform deep hybrid NLP analysis between a single candidate resume and job description.
    Returns calibrated ATS Compatibility Score, Fit Tier, Matched/Missing Skills, and Actionable Feedback.
    """
    try:
        match_result = matcher_service.analyze_match(
            resume_text=request.resume_text,
            jd_text=request.jd_text
        )
        return SingleMatchResponse(
            status="success",
            job_title=request.job_title or "Target Position",
            match_result=match_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error during matching: {str(e)}")

@app.post("/api/v1/match-jobs", response_model=BatchMatchResponse, tags=["Global Job Discovery"])
async def match_against_jobs(request: BatchMatchRequest):
    """
    Match candidate resume against multiple global jobs and return ranked results sorted by compatibility score.
    """
    try:
        ranked_results = matcher_service.match_against_global_jobs(
            resume_text=request.resume_text,
            specific_job_ids=request.job_ids
        )
        return BatchMatchResponse(
            status="success",
            total_jobs_evaluated=len(ranked_results),
            ranked_jobs=ranked_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ranking global jobs: {str(e)}")

# ----------------------------------------------------
# SERVE FRONTEND STATIC FILES
# ----------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", tags=["Frontend"])
    async def serve_frontend():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Alture AI FastAPI Backend is running. Open /docs for Swagger API."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Alture AI FastAPI Production Server on http://localhost:{port}")
    uvicorn.run("deployment.backend.main:app", host="0.0.0.0", port=port, reload=True)
