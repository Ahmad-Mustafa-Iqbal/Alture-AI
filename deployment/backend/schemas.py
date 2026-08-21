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
    jd_text: str
    required_skills: List[str] = []

class BatchMatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Raw text of the candidate's resume")
    job_ids: Optional[List[str]] = Field(None, description="Optional list of specific job IDs to match against")

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
    salary_range: Optional[str]
    ats_score: float
    fit_tier: str
    matched_skills_count: int
    missing_skills_count: int
    matched_skills_sample: List[str]
    missing_skills_sample: List[str]

class BatchMatchResponse(BaseModel):
    status: str = "success"
    total_jobs_evaluated: int
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
