from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SingleMatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Raw text of the candidate's resume")
    jd_text: str = Field(..., min_length=20, description="Raw text of the target job description")
    job_title: Optional[str] = Field("Target Job Position", description="Optional title of the target position")

class JobPosting(BaseModel):
    id: str
    title: str
    company: str
    location: str
    type: str  # Remote, Hybrid, On-site
    salary_range: Optional[str] = None
    apply_url: Optional[str] = None
    jd_text: str
    required_skills: List[str] = []

class BatchMatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Raw text of the candidate's resume")
    job_ids: Optional[List[str]] = Field(None, description="Optional list of specific job IDs to match against")

class LiveJobSearchRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Candidate resume text to match against")
    query: Optional[str] = Field("Software Engineer", description="Job search keyword e.g. 'AI Engineer', 'Python', 'React'")
    location: Optional[str] = Field("Pakistan", description="Location e.g. 'Pakistan', 'Lahore', 'Karachi', 'Remote', 'USA'")
    provider: Optional[str] = Field("auto", description="'auto' | 'jsearch' | 'remotive'")
    rapidapi_key: Optional[str] = Field(None, description="Optional user-provided RapidAPI key for unlimited live LinkedIn/Indeed queries")
    limit: Optional[int] = Field(15, description="Number of job postings to retrieve and match")

class SkillAnalysis(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    candidate_skills: List[str]
    jd_skills: List[str]
    skill_jaccard_score: float
    skill_recall_score: float

class MatchResult(BaseModel):
    ats_score: float = Field(..., description="Calibrated compatibility score from 0 to 100")
    fit_tier: str = Field(..., description="'Good Fit' | 'Potential Fit' | 'No Fit'")
    fit_confidence: float = Field(..., description="Probability confidence for the assigned tier")
    semantic_similarity: float = Field(..., description="Sentence-BERT cosine similarity (0 to 1)")
    cross_encoder_score: Optional[float] = Field(None, description="Pairwise cross-attention relevance score")
    skill_analysis: SkillAnalysis
    recommendations: List[str]
    word_count_ratio: float
    resume_word_count: int
    jd_word_count: int

class SingleMatchResponse(BaseModel):
    status: str = "success"
    job_title: str
    match_result: MatchResult

class RankedJobMatch(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    type: str
    salary_range: Optional[str] = None
    apply_url: Optional[str] = None
    ats_score: float
    fit_tier: str
    matched_skills_count: int
    missing_skills_count: int
    matched_skills_sample: List[str]
    missing_skills_sample: List[str]

class BatchMatchResponse(BaseModel):
    status: str = "success"
    total_jobs_evaluated: int
    provider_used: str = "Multi-Source Engine"
    search_query: Optional[str] = None
    search_location: Optional[str] = None
    ranked_jobs: List[RankedJobMatch]

class SamplePersona(BaseModel):
    id: str
    name: str
    title: str
    summary: str
    resume_text: str

class SampleDataResponse(BaseModel):
    personas: List[SamplePersona]
    jobs: List[JobPosting]

# ─── AI Coach Schemas ───
class AICoachRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Candidate resume text")
    job_title: str = Field("Software Engineer", description="Target job title")
    job_description: str = Field("", description="Job description text")
    company: str = Field("", description="Company name")
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    ats_score: float = Field(0.0, description="Current ATS score")
    action: str = Field("tips", description="'tips' | 'cover_letter' | 'interview_prep'")

class AICoachResponse(BaseModel):
    status: str = "success"
    action: str
    powered_by: str = "gemini-2.0-flash"
    data: Dict[str, Any]

# ─── PDF Report Schema ───
class ATSReportRequest(BaseModel):
    candidate_name: str = "Candidate"
    job_title: str = "Target Position"
    company: str = "Company"
    location: str = "Pakistan"
    ats_score: float = 0.0
    fit_tier: str = "Potential Fit"
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    tips: Optional[List[Dict[str, Any]]] = None
    overall_assessment: Optional[str] = ""
