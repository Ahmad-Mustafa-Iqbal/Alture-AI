import re
import urllib.request
import json
from typing import List
from .schemas import JobPosting
from .sample_data import SAMPLE_JOBS

def clean_html(raw_html: str) -> str:
    """Strip HTML tags and unescape common HTML entities."""
    clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
    clean_text = clean_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', clean_text).strip()

def fetch_live_global_jobs(limit: int = 15) -> List[JobPosting]:
    """
    Fetch real-time live remote tech jobs from the public Remotive API.
    Gracefully falls back to curated sample jobs if offline.
    """
    url = f"https://remotive.com/api/remote-jobs?category=software-dev&limit={limit}"
    headers = {"User-Agent": "Alture-AI-Engine/2.0"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as res:
            if res.status == 200:
                data = json.loads(res.read().decode('utf-8'))
                raw_jobs = data.get("jobs", [])
                
                live_jobs = []
                for j in raw_jobs[:limit]:
                    job_id = f"live-{j.get('id', '')}"
                    title = j.get('title', 'Software Engineer')
                    company = j.get('company_name', 'Global Tech Co')
                    location = j.get('candidate_required_location', 'Worldwide Remote')
                    salary = j.get('salary', '') or "$120k - $180k"
                    tags = j.get('tags', [])
                    description_clean = clean_html(j.get('description', ''))
                    
                    if len(description_clean) < 100:
                        description_clean = f"Position: {title} at {company}. Required skills: {', '.join(tags)}."

                    live_jobs.append(JobPosting(
                        id=job_id,
                        title=title,
                        company=company,
                        location=f"Remote ({location})" if "Remote" not in location else location,
                        type="Remote",
                        salary_range=salary if salary else None,
                        required_skills=tags[:8],
                        jd_text=description_clean
                    ))
                
                if live_jobs:
                    print(f"  [OK] Successfully fetched {len(live_jobs)} live real-world jobs from Remotive API.")
                    return live_jobs
    except Exception as e:
        print(f"  [WARN] Live job API request failed ({e}). Using curated fallback repository.")
    
    return SAMPLE_JOBS
