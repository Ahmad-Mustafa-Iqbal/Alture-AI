"""
feature_extraction.py — Feature extraction: TF-IDF, Sentence-BERT, and Skill Extraction.

Implements three feature extraction strategies:
1. TF-IDF vectorization for keyword-based matching
2. Sentence-BERT embeddings for semantic similarity
3. Skill extraction using spaCy + custom skill dictionary
"""

import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
import joblib


# 1. TF-IDF Features
class TFIDFFeatureExtractor:
    """
    Extract TF-IDF features from resume and job description text.

    Concatenates TF-IDF vectors from both texts and also computes
    cosine similarity between them.
    """

    def __init__(self, max_features: int = 5000, ngram_range: tuple = (1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.resume_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words="english",
            sublinear_tf=True,
        )
        self.jd_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words="english",
            sublinear_tf=True,
        )
        self._fitted = False

    def fit(self, df: pd.DataFrame) -> "TFIDFFeatureExtractor":
        """Fit TF-IDF vectorizers on training data."""
        resume_col = "resume_clean" if "resume_clean" in df.columns else "resume_text"
        jd_col = "jd_clean" if "jd_clean" in df.columns else "jd_text"

        self.resume_vectorizer.fit(df[resume_col].fillna(""))
        self.jd_vectorizer.fit(df[jd_col].fillna(""))
        self._fitted = True
        print(f"  [INFO] TF-IDF fitted: resume vocab={len(self.resume_vectorizer.vocabulary_)}, "
              f"JD vocab={len(self.jd_vectorizer.vocabulary_)}")
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform text to TF-IDF feature matrix (concatenated)."""
        if not self._fitted:
            raise RuntimeError("Call fit() before transform().")

        resume_col = "resume_clean" if "resume_clean" in df.columns else "resume_text"
        jd_col = "jd_clean" if "jd_clean" in df.columns else "jd_text"

        resume_tfidf = self.resume_vectorizer.transform(df[resume_col].fillna(""))
        jd_tfidf = self.jd_vectorizer.transform(df[jd_col].fillna(""))

        # Cosine similarity between resume and JD TF-IDF vectors
        from sklearn.metrics.pairwise import cosine_similarity
        cos_sim = np.array([
            cosine_similarity(resume_tfidf[i], jd_tfidf[i])[0, 0]
            for i in range(resume_tfidf.shape[0])
        ]).reshape(-1, 1)

        # Concatenate: resume_tfidf + jd_tfidf + cosine_similarity
        combined = hstack([resume_tfidf, jd_tfidf]).toarray()
        return np.hstack([combined, cos_sim])

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(df)
        return self.transform(df)

    def save(self, path: str) -> None:
        """Save fitted vectorizers."""
        joblib.dump({
            "resume_vectorizer": self.resume_vectorizer,
            "jd_vectorizer": self.jd_vectorizer,
            "max_features": self.max_features,
            "ngram_range": self.ngram_range,
        }, path)
        print(f"  [INFO] TF-IDF extractor saved to {path}")

    @classmethod
    def load(cls, path: str) -> "TFIDFFeatureExtractor":
        """Load fitted vectorizers."""
        data = joblib.load(path)
        extractor = cls(data["max_features"], data["ngram_range"])
        extractor.resume_vectorizer = data["resume_vectorizer"]
        extractor.jd_vectorizer = data["jd_vectorizer"]
        extractor._fitted = True
        return extractor


# 2. Sentence-BERT Features
class SBERTFeatureExtractor:
    """
    Extract semantic features using Sentence-BERT.

    Uses the `all-MiniLM-L6-v2` model (lightweight, ~80MB) to encode
    resume and job description texts, then computes cosine similarity.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None

    def _load_model(self):
        """Lazy-load the model to avoid import overhead."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            print(f"  [INFO] Loading Sentence-BERT model: {self.model_name} ...")
            self._model = SentenceTransformer(self.model_name)
            print(f"  [INFO] Model loaded successfully.")
        return self._model

    def encode_texts(self, texts: list, desc: str = "Encoding") -> np.ndarray:
        """Encode a list of texts into embeddings."""
        model = self._load_model()
        print(f"  [INFO] {desc} {len(texts)} texts ...")
        embeddings = model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
        )
        return embeddings

    def extract_features(self, df: pd.DataFrame) -> dict:
        """
        Extract SBERT features: embeddings and cosine similarity.

        Returns
        -------
        dict with keys:
          - resume_embeddings: np.ndarray (n_samples, embedding_dim)
          - jd_embeddings: np.ndarray (n_samples, embedding_dim)
          - cosine_similarities: np.ndarray (n_samples,)
        """
        resume_col = "resume_clean" if "resume_clean" in df.columns else "resume_text"
        jd_col = "jd_clean" if "jd_clean" in df.columns else "jd_text"

        resume_embs = self.encode_texts(df[resume_col].fillna("").tolist(), "Resume")
        jd_embs = self.encode_texts(df[jd_col].fillna("").tolist(), "JD")

        # Cosine similarity (row-wise)
        from sklearn.metrics.pairwise import cosine_similarity as cos_sim_fn
        cos_sims = np.array([
            cos_sim_fn(resume_embs[i:i+1], jd_embs[i:i+1])[0, 0]
            for i in range(len(resume_embs))
        ])

        print(f"  [INFO] SBERT features extracted. Mean cosine similarity: {cos_sims.mean():.4f}")

        return {
            "resume_embeddings": resume_embs,
            "jd_embeddings": jd_embs,
            "cosine_similarities": cos_sims,
        }


# 3. Skill Extraction
# Curated list of technical and soft skills for extraction
TECH_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "rust", "scala", "kotlin", "swift", "php", "r", "matlab", "perl",
    # Web & Frameworks
    "react", "angular", "vue", "node.js", "nodejs", "django", "flask",
    "spring", "express", "fastapi", "next.js", "nextjs",
    # Data Science & ML
    "machine learning", "deep learning", "natural language processing", "nlp",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
    "sklearn", "pandas", "numpy", "spark", "hadoop", "data analysis",
    "data science", "statistical analysis", "data mining", "ai",
    "artificial intelligence", "neural network", "neural networks",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "ci/cd", "jenkins", "terraform", "ansible",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "oracle", "nosql", "database", "cassandra",
    # Tools & Practices
    "git", "github", "jira", "agile", "scrum", "rest api", "graphql",
    "microservices", "linux", "excel", "power bi", "tableau",
    # Other Tech
    "html", "css", "api", "etl", "data warehouse", "big data",
    "blockchain", "iot", "cybersecurity", "devops", "cloud computing",
}

SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving",
    "problem-solving", "critical thinking", "time management",
    "project management", "analytical", "collaboration", "adaptability",
    "creativity", "attention to detail", "organization", "management",
    "mentoring", "strategic planning", "decision making", "negotiation",
    "presentation", "stakeholder management", "cross-functional",
}

ALL_SKILLS = TECH_SKILLS | SOFT_SKILLS


def extract_skills(text: str, skill_set: set | None = None) -> set:
    """
    Extract skills from text using keyword matching against the skill dictionary.

    Parameters
    ----------
    text : The text to extract skills from.
    skill_set : Set of skills to look for. Defaults to ALL_SKILLS.

    Returns
    -------
    Set of matched skills (lowercased).
    """
    if skill_set is None:
        skill_set = ALL_SKILLS

    text_lower = str(text).lower()
    found = set()
    for skill in skill_set:
        if skill in text_lower:
            found.add(skill)
    return found


def compute_skill_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute skill-based features for each resume–JD pair.

    Features created:
    - resume_skills_count: Number of skills found in resume
    - jd_skills_count: Number of skills found in JD
    - matched_skills_count: Skills present in both resume and JD
    - missing_skills_count: Skills in JD but not in resume
    - skill_match_ratio: matched / jd_skills (0 if JD has no skills)
    - matched_skills: List of matched skill names (for explainability)
    - missing_skills: List of missing skill names (for explainability)
    """
    df = df.copy()

    resume_col = "resume_text" if "resume_text" in df.columns else "text"
    jd_col = "jd_text" if "jd_text" in df.columns else "text"

    results = []
    for _, row in df.iterrows():
        resume_skills = extract_skills(row[resume_col])
        jd_skills = extract_skills(row[jd_col])
        matched = resume_skills & jd_skills
        missing = jd_skills - resume_skills

        results.append({
            "resume_skills_count": len(resume_skills),
            "jd_skills_count": len(jd_skills),
            "matched_skills_count": len(matched),
            "missing_skills_count": len(missing),
            "skill_match_ratio": len(matched) / max(len(jd_skills), 1),
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
        })

    skill_df = pd.DataFrame(results, index=df.index)
    for col in skill_df.columns:
        df[col] = skill_df[col]

    print(f"  [INFO] Skill features computed. Mean skill match ratio: "
          f"{df['skill_match_ratio'].mean():.4f}")

    return df


if __name__ == "__main__":
    # Quick test
    test_resume = "Experienced Python developer with expertise in machine learning and tensorflow"
    test_jd = "Looking for a Python developer with machine learning, deep learning, and aws experience"

    resume_skills = extract_skills(test_resume)
    jd_skills = extract_skills(test_jd)
    print(f"Resume skills: {resume_skills}")
    print(f"JD skills:     {jd_skills}")
    print(f"Matched:       {resume_skills & jd_skills}")
    print(f"Missing:       {jd_skills - resume_skills}")
