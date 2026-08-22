import os
from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from .schemas import (
    SingleMatchRequest, SingleMatchResponse,
    BatchMatchRequest, BatchMatchResponse,
    LiveJobSearchRequest, SampleDataResponse,
    AICoachRequest, AICoachResponse,
    ATSReportRequest
)
from .matcher_service import matcher_service
from .sample_data import SAMPLE_PERSONAS, SAMPLE_JOBS
from .resume_parser import parse_resume_file
from .gemini_coach_service import coach_service
from .pdf_report_service import generate_ats_audit_pdf

app = FastAPI(
    title="Alture AI Backend",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "SentenceTransformer + XGBoost",
        "version": "2.0.0"
    }

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        parsed_result = parse_resume_file(filename=file.filename, file_bytes=contents)
        if parsed_result["word_count"] < 10:
            raise HTTPException(status_code=400, detail="Could not extract text from document.")
            
        return parsed_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@router.get("/sample-data", response_model=SampleDataResponse)
async def get_sample_data():
    return SampleDataResponse(
        personas=SAMPLE_PERSONAS,
        jobs=SAMPLE_JOBS
    )

@router.post("/analyze", response_model=SingleMatchResponse)
async def analyze_single_match(request: SingleMatchRequest):
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

@router.post("/match-jobs", response_model=BatchMatchResponse)
async def match_against_jobs(request: BatchMatchRequest):
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
        raise HTTPException(status_code=500, detail=f"Error ranking jobs: {str(e)}")

@router.get("/jobs/live")
async def get_live_jobs(limit: int = 15):
    from .live_jobs_service import fetch_live_global_jobs
    live_jobs = fetch_live_global_jobs(limit=limit)
    return {"status": "success", "count": len(live_jobs), "jobs": live_jobs}

@router.post("/search-and-match-jobs", response_model=BatchMatchResponse)
async def search_and_match_jobs(request: LiveJobSearchRequest):
    from .live_jobs_service import fetch_multi_source_jobs
    try:
        jobs, provider_name = fetch_multi_source_jobs(
            query=request.query or "Software Engineer",
            location=request.location or "Pakistan",
            provider=request.provider or "auto",
            user_api_key=request.rapidapi_key,
            limit=request.limit or 15
        )
        ranked_results = matcher_service.match_against_jobs_list(
            resume_text=request.resume_text,
            jobs=jobs
        )
        return BatchMatchResponse(
            status="success",
            total_jobs_evaluated=len(ranked_results),
            provider_used=provider_name,
            search_query=request.query,
            search_location=request.location,
            ranked_jobs=ranked_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

@router.post("/ai-coach", response_model=AICoachResponse)
async def ai_career_coach(request: AICoachRequest):
    try:
        if request.action == "tips":
            result = coach_service.get_resume_tips(
                resume_text=request.resume_text,
                job_title=request.job_title,
                job_description=request.job_description,
                matched_skills=request.matched_skills,
                missing_skills=request.missing_skills,
                ats_score=request.ats_score
            )
        elif request.action == "cover_letter":
            result = coach_service.generate_cover_letter(
                resume_text=request.resume_text,
                job_title=request.job_title,
                company=request.company,
                job_description=request.job_description
            )
        elif request.action == "interview_prep":
            result = coach_service.generate_interview_questions(
                job_title=request.job_title,
                job_description=request.job_description,
                missing_skills=request.missing_skills,
                matched_skills=request.matched_skills
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")

        return AICoachResponse(
            status="success",
            action=request.action,
            powered_by=result.get("powered_by", "gemini-2.0-flash"),
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Coach error: {str(e)}")

@router.post("/download-ats-report")
async def download_ats_audit_report(request: ATSReportRequest):
    try:
        pdf_bytes = generate_ats_audit_pdf(
            candidate_name=request.candidate_name or "Candidate",
            job_title=request.job_title or "Target Position",
            company=request.company or "Tech Company",
            location=request.location or "Pakistan",
            ats_score=request.ats_score,
            fit_tier=request.fit_tier,
            matched_skills=request.matched_skills or [],
            missing_skills=request.missing_skills or [],
            actionable_feedback=request.actionable_feedback or []
        )
        safe_filename = f"ATS_Report_{request.candidate_name.replace(' ', '_')}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

# Mount endpoints under both /v1 and /api/v1
app.include_router(router, prefix="/v1")
app.include_router(router, prefix="/api/v1")

# Static frontend assets
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Alture AI Backend Active"}
