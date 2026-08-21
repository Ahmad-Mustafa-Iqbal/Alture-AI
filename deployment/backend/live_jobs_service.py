import os
import re
import json
import urllib.request
import urllib.parse
from typing import List, Tuple
from .schemas import JobPosting
from .sample_data import SAMPLE_JOBS

# Curated Pakistan Tech Roles for instant testing/fallback
PAKISTAN_TECH_JOBS: List[JobPosting] = [
    JobPosting(
        id="pk-sys-ai",
        title="Senior AI / Machine Learning Engineer",
        company="Systems Limited",
        location="Lahore, Pakistan (Hybrid / Remote)",
        type="Hybrid",
        salary_range="PKR 450,000 - 750,000 / month",
        apply_url="https://www.systemsltd.com/careers",
        required_skills=["python", "pytorch", "fastapi", "docker", "nlp", "llm", "transformers", "langchain", "aws"],
        jd_text="""Systems Limited is hiring a Senior AI/ML Engineer for our Enterprise Cognitive AI division in Lahore. 
Key Responsibilities:
• Design and implement enterprise Generative AI and NLP pipelines using PyTorch, Hugging Face Transformers, and LangChain.
• Develop low-latency REST APIs in Python using FastAPI and containerize services with Docker and Kubernetes.
• Build Retrieval-Augmented Generation (RAG) systems over vector databases (Pinecone, ChromaDB).
• Deploy and maintain scalable ML architectures on AWS cloud infrastructure.

Required Qualifications:
• 4+ years of professional AI/ML engineering experience.
• Strong expertise in Python, Scikit-Learn, PyTorch, and NLP architectures.
• Solid background in building production REST APIs using FastAPI and Docker.
• Familiarity with Git, Linux, and automated CI/CD."""
    ),
    JobPosting(
        id="pk-arbi-fullstack",
        title="Full-Stack Python & React Developer",
        company="Arbisoft",
        location="Lahore, Pakistan (Hybrid)",
        type="Hybrid",
        salary_range="PKR 350,000 - 550,000 / month",
        apply_url="https://arbisoft.com/careers",
        required_skills=["react", "python", "fastapi", "django", "typescript", "postgresql", "docker", "tailwind"],
        jd_text="""Arbisoft is looking for a talented Full-Stack Engineer with deep expertise in Python and modern React.
Key Responsibilities:
• Build modular, accessible frontend user interfaces in React, TypeScript, and modern styling frameworks.
• Develop robust, asynchronous backend services and REST APIs using FastAPI or Django.
• Optimize PostgreSQL database queries, data modeling, and Redis caching.
• Write clean unit and integration tests, participating in agile software delivery.

Requirements:
• 3+ years experience in Full-Stack software engineering.
• Deep proficiency with React and TypeScript.
• Strong backend experience with Python (FastAPI/Django).
• Experience with PostgreSQL, Docker, and Git."""
    ),
    JobPosting(
        id="pk-10p-devops",
        title="Senior Cloud DevOps & Kubernetes Engineer",
        company="10Pearls",
        location="Karachi / Islamabad, Pakistan",
        type="Remote",
        salary_range="PKR 400,000 - 650,000 / month",
        apply_url="https://10pearls.com/careers",
        required_skills=["kubernetes", "docker", "terraform", "aws", "ci/cd", "github actions", "linux", "python"],
        jd_text="""10Pearls is seeking a Senior DevOps / Cloud Infrastructure Engineer to lead cloud modernization.
Key Responsibilities:
• Architect, operate, and maintain production Kubernetes (EKS/GKE) clusters.
• Author Infrastructure as Code using Terraform and Ansible.
• Build automated CI/CD workflows using GitHub Actions and GitLab CI.
• Enforce cloud security compliance and infrastructure monitoring using Prometheus and Grafana.

Requirements:
• 4+ years in Cloud Infrastructure and DevOps.
• Strong mastery of Docker, Kubernetes, and AWS services.
• Scripting proficiency in Python or Bash."""
    ),
    JobPosting(
        id="pk-vd-data",
        title="Senior Data Platform Engineer",
        company="VentureDive",
        location="Lahore / Karachi, Pakistan",
        type="Remote",
        salary_range="PKR 380,000 - 600,000 / month",
        apply_url="https://venturedive.com/careers",
        required_skills=["python", "sql", "spark", "kafka", "postgresql", "airflow", "aws", "docker"],
        jd_text="""VentureDive is hiring a Data Platform Engineer to design real-time data pipelines.
Key Responsibilities:
• Build distributed data ingestion pipelines using Apache Spark and Python.
• Orchestrate ETL workflows using Apache Airflow.
• Optimize complex SQL queries and PostgreSQL data storage on AWS.

Requirements:
• 3+ years experience with Data Engineering, Python, Advanced SQL, and Spark."""
    )
]

def clean_html(raw_html: str) -> str:
    """Strip HTML tags and unescape common HTML entities."""
    clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
    clean_text = clean_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', clean_text).strip()

def search_jsearch_rapidapi(query: str, location: str, api_key: str, limit: int = 15) -> List[JobPosting]:
    """
    Query JSearch RapidAPI (LinkedIn, Indeed, Glassdoor, ZipRecruiter) for live jobs across Pakistan or worldwide.
    """
    search_term = f"{query} in {location}".strip()
    url = f"https://jsearch.p.rapidapi.com/search?query={urllib.parse.quote(search_term)}&num_pages=1"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        "User-Agent": "Alture-AI-Intelligence/2.0"
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        if res.status == 200:
            data = json.loads(res.read().decode('utf-8'))
            raw_jobs = data.get("data", [])
            
            parsed_jobs = []
            for j in raw_jobs[:limit]:
                job_id = f"jsearch-{j.get('job_id', '')}"
                title = j.get('job_title', query)
                company = j.get('employer_name', 'Global Employer')
                city = j.get('job_city', '')
                country = j.get('job_country', location)
                loc_str = f"{city}, {country}".strip(', ') if city else country
                if j.get('job_is_remote'):
                    loc_str = f"Remote ({loc_str})"
                
                apply_link = j.get('job_apply_link') or j.get('job_google_link')
                desc = j.get('job_description', '')
                desc_clean = clean_html(desc)
                
                # Extract highlights/skills if present
                req_skills = []
                highlights = j.get('job_highlights', {})
                if 'Qualifications' in highlights:
                    req_skills.extend([q[:30] for q in highlights['Qualifications'][:5]])

                parsed_jobs.append(JobPosting(
                    id=job_id,
                    title=title,
                    company=company,
                    location=loc_str,
                    type="Remote" if j.get('job_is_remote') else "On-site / Hybrid",
                    salary_range=j.get('job_salary_currency') or None,
                    apply_url=apply_link,
                    required_skills=req_skills,
                    jd_text=desc_clean if len(desc_clean) > 80 else f"{title} at {company} in {loc_str}. Requirements: {desc_clean}"
                ))
            return parsed_jobs
    return []

def search_remotive_api(query: str, limit: int = 15) -> List[JobPosting]:
    """
    Query Remotive Public API for worldwide live remote software/tech jobs.
    """
    category_param = "software-dev"
    url = f"https://remotive.com/api/remote-jobs?category={category_param}&limit={limit}"
    if query:
        url += f"&search={urllib.parse.quote(query)}"

    headers = {"User-Agent": "Alture-AI-Engine/2.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as res:
        if res.status == 200:
            data = json.loads(res.read().decode('utf-8'))
            raw_jobs = data.get("jobs", [])
            
            live_jobs = []
            for j in raw_jobs[:limit]:
                job_id = f"remotive-{j.get('id', '')}"
                title = j.get('title', 'Software Engineer')
                company = j.get('company_name', 'Global Tech Co')
                location = j.get('candidate_required_location', 'Worldwide Remote')
                salary = j.get('salary', '') or "$110k - $170k"
                tags = j.get('tags', [])
                apply_url = j.get('url', '')
                desc_clean = clean_html(j.get('description', ''))
                
                live_jobs.append(JobPosting(
                    id=job_id,
                    title=title,
                    company=company,
                    location=f"Remote ({location})" if "Remote" not in location else location,
                    type="Remote",
                    salary_range=salary if salary else None,
                    apply_url=apply_url,
                    required_skills=tags[:8],
                    jd_text=desc_clean
                ))
            return live_jobs
    return []

def fetch_multi_source_jobs(
    query: str = "Software Engineer",
    location: str = "Pakistan",
    provider: str = "auto",
    user_api_key: str = None,
    limit: int = 15
) -> Tuple[List[JobPosting], str]:
    """
    Multi-source job aggregator combining RapidAPI JSearch, Remotive, and Pakistan tech repository.
    Returns (jobs_list, provider_name_used).
    """
    api_key = user_api_key or os.environ.get("RAPIDAPI_KEY")
    
    # 1. Try JSearch RapidAPI if key is provided
    if api_key and (provider in ["auto", "jsearch"]):
        try:
            jobs = search_jsearch_rapidapi(query=query, location=location, api_key=api_key, limit=limit)
            if jobs:
                return jobs, "JSearch (Live LinkedIn, Indeed & Glassdoor)"
        except Exception as e:
            print(f"  [WARN] JSearch RapidAPI query failed: {e}. Falling back to secondary engine.")

    # 2. If location is Pakistan and no API key, return curated Pakistan tech jobs
    if "pakistan" in location.lower() or "lahore" in location.lower() or "karachi" in location.lower() or "islamabad" in location.lower():
        # Filter matching query keyword
        q_lower = query.lower()
        matched_pk = [j for j in PAKISTAN_TECH_JOBS if any(word in j.title.lower() or word in j.jd_text.lower() for word in q_lower.split())]
        if not matched_pk:
            matched_pk = PAKISTAN_TECH_JOBS
        return matched_pk, "Pakistan Enterprise Tech Feed (Systems, Arbisoft, 10Pearls)"

    # 3. Otherwise, search Worldwide Remotive API
    try:
        jobs = search_remotive_api(query=query, limit=limit)
        if jobs:
            return jobs, "Remotive Worldwide Remote Stream"
    except Exception as e:
        print(f"  [WARN] Remotive API query failed: {e}.")

    # 4. Final Fallback
    return SAMPLE_JOBS, "Curated Global Benchmark Repository"
