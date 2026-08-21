import os
import sys
import json
import numpy as np
import joblib
import gradio as gr

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEPLOYMENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DEPLOYMENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from src.feature_extraction import extract_skills, ALL_SKILLS, TECH_SKILLS, SOFT_SKILLS

print("[INFO] Loading models...")

# Load the hybrid XGBoost model
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "hybrid_xgboost_tuned.joblib")
if os.path.exists(MODEL_PATH):
    hybrid_model = joblib.load(MODEL_PATH)
    print(f"  [OK] Hybrid model loaded from {MODEL_PATH}")
else:
    hybrid_model = None
    print(f"  [WARN] Hybrid model not found at {MODEL_PATH}")
    print("     Run notebooks first or download from Colab.")

# Load Sentence-BERT
print("[INFO] Loading Sentence-BERT model ...")
from sentence_transformers import SentenceTransformer
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
print("  [OK] Sentence-BERT model loaded")


# Prediction Function
def predict_match(resume_text: str, jd_text: str) -> tuple:
    """
    Predict ATS compatibility between a resume and job description.

    Returns
    -------
    tuple of (score_text, category_text, matched_skills_text,
              missing_skills_text, similarity_text, details_text)
    """
    if not resume_text.strip() or not jd_text.strip():
        return ("⚠️ Please enter both resume and job description text.",
                "", "", "", "", "")

    # ── Signal 1: Semantic Similarity ──
    resume_emb = sbert_model.encode([resume_text], convert_to_numpy=True)
    jd_emb = sbert_model.encode([jd_text], convert_to_numpy=True)

    from sklearn.metrics.pairwise import cosine_similarity
    cos_sim = cosine_similarity(resume_emb, jd_emb)[0, 0]
    emb_diff = np.abs(resume_emb - jd_emb)

    # ── Signal 2: Skill Extraction ──
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    extra = sorted(resume_skills - jd_skills)

    skill_match_ratio = len(matched) / max(len(jd_skills), 1)

    # ── Signal 3: Structured Features ──
    resume_char_len = len(resume_text)
    jd_char_len = len(jd_text)
    resume_word_count = len(resume_text.split())
    jd_word_count = len(jd_text.split())
    length_ratio = resume_char_len / max(jd_char_len, 1)

    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    keyword_overlap = len(resume_words & jd_words) / max(len(jd_words), 1)

    # ── Build feature vector ──
    features = np.hstack([
        np.array([[cos_sim]]),
        emb_diff,
        np.array([[len(resume_skills), len(jd_skills), len(matched),
                   len(missing), skill_match_ratio]]),
        np.array([[resume_char_len, jd_char_len, resume_word_count,
                   jd_word_count, length_ratio, keyword_overlap]]),
    ])
    features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

    # ── Predict ──
    if hybrid_model is not None:
        ats_score = float(hybrid_model.predict(features)[0])
    else:
        # Fallback: use cosine similarity as a rough score
        ats_score = cos_sim * 100

    # Clamp to valid range
    ats_score = max(0, min(100, ats_score))

    # Determine category
    if ats_score >= 65:
        category = "✅ Good Fit"
        cat_color = "green"
    elif ats_score >= 40:
        category = "⚠️ Potential Fit"
        cat_color = "orange"
    else:
        category = "❌ No Fit"
        cat_color = "red"

    # ── Format outputs ──
    score_text = f"## 🎯 ATS Score: {ats_score:.1f} / 100"

    category_text = f"### Category: {category}"

    matched_text = "### ✅ Matched Skills\n"
    if matched:
        matched_text += "\n".join([f"- {s}" for s in matched])
    else:
        matched_text += "_No matching skills detected._"

    missing_text = "### ❌ Missing Skills\n"
    if missing:
        missing_text += "\n".join([f"- **{s}**" for s in missing])
    else:
        missing_text += "_No missing skills — great match!_"

    similarity_text = f"### 📊 Semantic Similarity: {cos_sim:.4f}"

    details_text = (
        f"### 📋 Detailed Analysis\n"
        f"- **Resume skills found**: {len(resume_skills)}\n"
        f"- **JD skills required**: {len(jd_skills)}\n"
        f"- **Skills matched**: {len(matched)} ({skill_match_ratio*100:.1f}%)\n"
        f"- **Skills missing**: {len(missing)}\n"
        f"- **Extra skills**: {len(extra)}\n"
        f"- **Keyword overlap**: {keyword_overlap*100:.1f}%\n"
        f"- **Resume length**: {resume_word_count} words\n"
        f"- **JD length**: {jd_word_count} words\n"
    )

    if extra:
        details_text += f"\n### 💡 Extra Skills (in resume, not in JD)\n"
        details_text += "\n".join([f"- {s}" for s in extra[:15]])

    return score_text, category_text, matched_text, missing_text, similarity_text, details_text


# Sample Data
SAMPLE_RESUME = """Senior Software Engineer with 7 years of experience in Python, JavaScript, and cloud 
technologies. Skilled in machine learning, data analysis, and building scalable web applications. 
Proficient in Django, React, AWS, Docker, and CI/CD pipelines. Led a team of 5 developers to 
deliver a recommendation engine that increased user engagement by 25%. Strong background in 
agile methodologies, git version control, and SQL databases. Master's degree in Computer Science.
Experience with TensorFlow, scikit-learn, and natural language processing. Excellent communication 
and problem-solving skills."""

SAMPLE_JD = """We are looking for a Machine Learning Engineer with strong Python skills and experience 
in deep learning frameworks (TensorFlow, PyTorch). The ideal candidate will have:
- 5+ years of experience in software development
- Strong knowledge of machine learning and data science
- Experience with cloud platforms (AWS, GCP, or Azure)
- Proficiency in SQL and NoSQL databases
- Experience with Docker and Kubernetes for deployment
- Knowledge of NLP and computer vision
- Excellent leadership and communication skills
- Experience with agile development and CI/CD
- Bachelor's or Master's in Computer Science or related field"""


# Gradio Interface
def create_app():
    """Create and configure the Gradio interface."""

    with gr.Blocks(
        title="Resume–Job Matching System",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="green",
        ),
        css="""
            .main-title { text-align: center; margin-bottom: 10px; }
            .output-box { min-height: 200px; }
        """,
    ) as app:

        gr.Markdown(
            """
            # 🎯 Resume–Job Matching System
            ### Hybrid NLP-Based ATS Compatibility Analyzer

            Paste your **resume** and a **job description** below to get an instant
            ATS compatibility score with detailed skill-level feedback.

            *Powered by Sentence-BERT semantic matching + Skill extraction + XGBoost*
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                resume_input = gr.Textbox(
                    label="📄 Resume Text",
                    placeholder="Paste your resume text here ...",
                    lines=12,
                    value=SAMPLE_RESUME,
                )
            with gr.Column(scale=1):
                jd_input = gr.Textbox(
                    label="💼 Job Description",
                    placeholder="Paste the job description here ...",
                    lines=12,
                    value=SAMPLE_JD,
                )

        analyze_btn = gr.Button("🔍 Analyze Match", variant="primary", size="lg")

        with gr.Row():
            with gr.Column(scale=1):
                score_output = gr.Markdown(label="ATS Score")
                category_output = gr.Markdown(label="Category")
                similarity_output = gr.Markdown(label="Semantic Similarity")

            with gr.Column(scale=1):
                matched_output = gr.Markdown(label="Matched Skills")
                missing_output = gr.Markdown(label="Missing Skills")

        details_output = gr.Markdown(label="Detailed Analysis")

        # Connect button
        analyze_btn.click(
            fn=predict_match,
            inputs=[resume_input, jd_input],
            outputs=[score_output, category_output, matched_output,
                     missing_output, similarity_output, details_output],
        )

        gr.Markdown(
            """
            ---
            **Capstone Project** — Hybrid NLP-Based Job Recommendation & Resume–Job Matching System

            *Built with Sentence-BERT (all-MiniLM-L6-v2), spaCy skill extraction, and XGBoost*
            """
        )

    return app


# Main
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LAUNCHING RESUME–JOB MATCHING SYSTEM")
    print("=" * 60)
    print("  URL: http://localhost:7860")
    print("  Press Ctrl+C to stop the server.\n")

    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
