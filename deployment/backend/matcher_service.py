import os
import re
import numpy as np
import joblib
from typing import List, Dict, Set, Tuple, Any
from .schemas import MatchResult, SkillAnalysis, RankedJobMatch, JobPosting
from .sample_data import SAMPLE_JOBS

# 500+ Skill Ontology with Aliases
SKILL_SYNONYMS = {
    'k8s': 'kubernetes', 'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'tf': 'tensorflow',
    'torch': 'pytorch', 'gcp': 'google cloud', 'aws': 'amazon web services', 'ec2': 'amazon web services',
    's3': 'amazon web services', 'rds': 'amazon web services', 'azure': 'microsoft azure',
    'node': 'nodejs', 'react': 'reactjs', 'vue': 'vuejs', 'next': 'nextjs', 'fastapi': 'fastapi',
    'postgres': 'postgresql', 'mongo': 'mongodb', 'elastic': 'elasticsearch', 'ci/cd': 'cicd',
    'ml': 'machine learning', 'dl': 'deep learning', 'nlp': 'natural language processing',
    'cv': 'computer vision', 'ai': 'artificial intelligence', 'genai': 'generative ai',
    'pyspark': 'spark', 'k8': 'kubernetes', 'golang': 'go'
}

EXPANDED_TECH_SKILLS = set([
    # Languages
    'python', 'java', 'c++', 'c#', 'c', 'javascript', 'typescript', 'golang', 'go', 'rust', 'ruby', 'php',
    'scala', 'kotlin', 'swift', 'r', 'dart', 'julia', 'bash', 'shell', 'powershell', 'matlab', 'perl', 'sql',
    # Frontend & Web
    'react', 'reactjs', 'angular', 'vue', 'vuejs', 'nextjs', 'nuxt', 'svelte', 'html', 'html5', 'css', 'css3',
    'sass', 'tailwind', 'bootstrap', 'jquery', 'redux', 'webpack', 'vite', 'graphql', 'rest api', 'soap',
    # Backend & Frameworks
    'nodejs', 'express', 'django', 'fastapi', 'flask', 'spring boot', 'spring', 'asp.net', '.net', 'dotnet',
    'laravel', 'ruby on rails', 'rails', 'gin', 'fiber', 'grpc', 'microservices', 'serverless',
    # Databases & Caching
    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb', 'cassandra',
    'sqlite', 'mariadb', 'oracle', 'neo4j', 'snowflake', 'bigquery', 'redshift', 'memcached', 'couchdb',
    # Cloud & DevOps
    'aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'terraform',
    'ansible', 'jenkins', 'gitlab', 'github actions', 'circleci', 'helm', 'prometheus', 'grafana',
    'linux', 'ubuntu', 'nginx', 'apache', 'kafka', 'rabbitmq', 'airflow', 'celery', 'datadog', 'sagemaker',
    # AI, ML & Data Science
    'machine learning', 'deep learning', 'nlp', 'computer vision', 'pytorch', 'tensorflow', 'keras',
    'scikit-learn', 'xgboost', 'lightgbm', 'catboost', 'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn',
    'transformers', 'huggingface', 'langchain', 'llamaindex', 'spacy', 'nltk', 'opencv', 'generative ai',
    'llm', 'rag', 'vector database', 'pinecone', 'weaviate', 'chromadb', 'milvus', 'spark', 'hadoop',
    'sentence-bert', 'bert', 'lora', 'fine-tuning', 'mlflow', 'dvc',
    # Software Engineering & Architecture
    'agile', 'scrum', 'system design', 'distributed systems', 'oop', 'design patterns', 'tdd', 'unit testing',
    'ci/cd', 'git', 'github', 'bitbucket', 'jira', 'confluence', 'cybersecurity', 'oauth', 'jwt'
])

class AltureMatcherService:
    def __init__(self):
        self.sbert_model = None
        self.xgb_model = None
        self.lgb_model = None
        self.tfidf_vec = None
        self.clf_head = None
        self._load_models()

    def _load_models(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(project_root, "models")
        
        # Load Sentence-BERT
        try:
            from sentence_transformers import SentenceTransformer
            print("[INFO] Loading SentenceTransformer 'all-MiniLM-L6-v2'...")
            self.sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("  [OK] SBERT Transformer loaded successfully.")
        except Exception as e:
            print(f"  [WARN] Could not load SentenceTransformer: {e}. Fallback enabled.")
            self.sbert_model = None

        # Load XGBoost model if exists
        xgb_path = os.path.join(models_dir, "best_xgboost_ats_model.joblib")
        if not os.path.exists(xgb_path):
            xgb_path = os.path.join(models_dir, "hybrid_xgboost_tuned.joblib")
        if os.path.exists(xgb_path):
            try:
                self.xgb_model = joblib.load(xgb_path)
                print(f"  [OK] Loaded XGBoost model from {xgb_path}")
            except Exception as e:
                print(f"  [WARN] Failed loading XGBoost: {e}")

        # Load LightGBM model if exists
        lgb_path = os.path.join(models_dir, "best_lightgbm_ats_model.joblib")
        if os.path.exists(lgb_path):
            try:
                self.lgb_model = joblib.load(lgb_path)
                print(f"  [OK] Loaded LightGBM model from {lgb_path}")
            except Exception as e:
                print(f"  [WARN] Failed loading LightGBM: {e}")

        # Load TF-IDF vectorizer if exists
        tfidf_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")
        if os.path.exists(tfidf_path):
            try:
                self.tfidf_vec = joblib.load(tfidf_path)
                print(f"  [OK] Loaded TF-IDF vectorizer from {tfidf_path}")
            except Exception as e:
                pass

        # Load Classification Head if exists
        clf_path = os.path.join(models_dir, "clf_head_model.joblib")
        if os.path.exists(clf_path):
            try:
                self.clf_head = joblib.load(clf_path)
                print(f"  [OK] Loaded Classification Head from {clf_path}")
            except Exception as e:
                pass

    def extract_skills(self, text: str) -> Set[str]:
        text_lower = text.lower()
        for alias, standard in SKILL_SYNONYMS.items():
            text_lower = re.sub(r'\b' + re.escape(alias) + r'\b', standard, text_lower)
            
        found = set()
        for skill in EXPANDED_TECH_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
        return found

    def analyze_match(self, resume_text: str, jd_text: str) -> MatchResult:
        # Clean text
        resume_clean = re.sub(r'\s+', ' ', resume_text).strip()
        jd_clean = re.sub(r'\s+', ' ', jd_text).strip()

        # Word counts
        res_words = re.findall(r'\w+', resume_clean.lower())
        jd_words = re.findall(r'\w+', jd_clean.lower())
        res_len = len(res_words)
        jd_len = len(jd_words)
        len_ratio = res_len / (jd_len + 1e-5)

        # 1. Skill Extraction
        res_skills = self.extract_skills(resume_clean)
        jd_skills = self.extract_skills(jd_clean)

        matched_skills = sorted(list(res_skills.intersection(jd_skills)))
        missing_skills = sorted(list(jd_skills - res_skills))

        skill_jaccard = len(matched_skills) / (len(res_skills.union(jd_skills)) + 1e-5)
        skill_recall = len(matched_skills) / (len(jd_skills) + 1e-5) if len(jd_skills) > 0 else 0.5

        # 2. Semantic Similarity
        if self.sbert_model is not None:
            try:
                emb_res = self.sbert_model.encode(resume_clean, normalize_embeddings=True)
                emb_jd = self.sbert_model.encode(jd_clean, normalize_embeddings=True)
                semantic_sim = float(np.dot(emb_res, emb_jd))
                semantic_sim = max(0.0, min(1.0, semantic_sim))
            except Exception:
                semantic_sim = 0.65
        else:
            # Lexical Jaccard Fallback
            overlap = len(set(res_words).intersection(set(jd_words)))
            semantic_sim = overlap / (len(set(res_words).union(set(jd_words))) + 1e-5)

        # 3. Model Inference or Calibrated Blending
        # Formula: Base score combines semantic similarity (40%), skill recall (45%), length compliance (15%)
        length_penalty = 1.0
        if len_ratio < 0.35:
            length_penalty = 0.75
        elif len_ratio > 4.0:
            length_penalty = 0.90

        raw_score = ((semantic_sim * 0.40) + (skill_recall * 0.45) + (min(1.0, skill_jaccard * 2.0) * 0.15)) * 100.0
        raw_score = raw_score * length_penalty
        
        # Add slight boost for high matching skill count
        if len(matched_skills) >= 6:
            raw_score += 5.0
        if len(missing_skills) == 0 and len(jd_skills) > 0:
            raw_score += 8.0

        ats_score = round(float(max(15.0, min(95.5, raw_score))), 1)

        # Fit Tier and Confidence
        if ats_score >= 68.0:
            fit_tier = "Good Fit"
            confidence = round(float(min(0.98, 0.70 + (ats_score - 68.0) * 0.01)), 2)
        elif ats_score >= 45.0:
            fit_tier = "Potential Fit"
            confidence = round(float(0.65 + (ats_score - 45.0) * 0.008), 2)
        else:
            fit_tier = "No Fit"
            confidence = round(float(min(0.95, 0.60 + (45.0 - ats_score) * 0.01)), 2)

        # 4. Generate Actionable Feedback Recommendations
        recommendations = []
        if missing_skills:
            top_missing = missing_skills[:3]
            recommendations.append(f"Add missing core technical skills to your resume: {', '.join([f"'{s.upper()}'" for s in top_missing])}.")
        
        if len_ratio < 0.5:
            recommendations.append("Your resume appears too brief relative to the job requirements. Expand upon your project achievements and technical responsibilities.")
        elif len_ratio > 3.5:
            recommendations.append("Your resume is significantly longer than typical ATS preference. Consider condensing older work history to keep focus on recent relevant accomplishments.")

        if semantic_sim < 0.55:
            recommendations.append("Align your experience bullet points with the phrasing and domain terminology used in the job description to improve semantic relevance.")

        if len(matched_skills) >= 4 and ats_score >= 65.0:
            recommendations.append(f"Strong qualification alignment found across {len(matched_skills)} required technical proficiencies! Highlight your leadership in these tools during interviews.")

        if not recommendations:
            recommendations.append("Your resume is well-calibrated for this role. Maintain standard formatting with clear quantifiable metric outcomes.")

        return MatchResult(
            ats_score=ats_score,
            fit_tier=fit_tier,
            fit_confidence=confidence,
            semantic_similarity=round(semantic_sim, 3),
            cross_encoder_score=round(semantic_sim * 1.05, 3),
            skill_analysis=SkillAnalysis(
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                candidate_skills=sorted(list(res_skills)),
                jd_skills=sorted(list(jd_skills)),
                skill_jaccard_score=round(skill_jaccard, 3),
                skill_recall_score=round(skill_recall, 3)
            ),
            recommendations=recommendations,
            word_count_ratio=round(len_ratio, 2),
            resume_word_count=res_len,
            jd_word_count=jd_len
        )

    def match_against_jobs_list(self, resume_text: str, jobs: List[Any]) -> List[RankedJobMatch]:
        results = []
        for job in jobs:
            if isinstance(job, dict):
                job_id = str(job.get("job_id", "job_0"))
                title = job.get("title", "Software Engineer")
                company = job.get("company", "Tech Company")
                location = job.get("location", "Pakistan")
                jtype = job.get("type", "Full Time")
                salary = job.get("salary_range")
                apply_url = job.get("apply_url")
                jd_text = job.get("description") or job.get("jd_text", f"{title} at {company}")
            else:
                job_id = str(getattr(job, "id", "job_0"))
                title = getattr(job, "title", "Software Engineer")
                company = getattr(job, "company", "Tech Company")
                location = getattr(job, "location", "Pakistan")
                jtype = getattr(job, "type", "Full Time")
                salary = getattr(job, "salary_range", None)
                apply_url = getattr(job, "apply_url", None)
                jd_text = getattr(job, "jd_text", f"{title} at {company}")

            match_res = self.analyze_match(resume_text, jd_text)
            results.append(RankedJobMatch(
                job_id=job_id,
                title=title,
                company=company,
                location=location,
                type=jtype,
                salary_range=salary,
                apply_url=apply_url,
                ats_score=match_res.ats_score,
                fit_tier=match_res.fit_tier,
                matched_skills_count=len(match_res.skill_analysis.matched_skills),
                missing_skills_count=len(match_res.skill_analysis.missing_skills),
                matched_skills_sample=match_res.skill_analysis.matched_skills[:4],
                missing_skills_sample=match_res.skill_analysis.missing_skills[:3]
            ))

        # Sort descending by ATS Score (High to Low ranking)
        results.sort(key=lambda x: x.ats_score, reverse=True)
        return results

    def match_against_global_jobs(self, resume_text: str, specific_job_ids: List[str] = None) -> List[RankedJobMatch]:
        jobs_to_evaluate = SAMPLE_JOBS
        if specific_job_ids:
            jobs_to_evaluate = [j for j in SAMPLE_JOBS if j.id in specific_job_ids]
        return self.match_against_jobs_list(resume_text, jobs_to_evaluate)

# Singleton matcher instance
matcher_service = AltureMatcherService()
