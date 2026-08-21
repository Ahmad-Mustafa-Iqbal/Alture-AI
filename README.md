---
title: Alture AI — Job Intelligence & Explainable ATS Engine
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Hybrid NLP Job Recommendation & ATS Engine
---

# Alture AI — Hybrid NLP-Based Job Recommendation and Resume–Job Matching System

## 📌 Problem Statement

Most job-search and ATS (Applicant Tracking System) tools match resumes to jobs by simply looking for matching keywords. This project builds a **smarter matching system** that understands the actual meaning behind a resume and a job description — not just the words used — and gives a clear, **explainable match score**.

The system combines three signal types:
1. **Semantic Similarity** — Sentence-BERT embeddings capture meaning beyond keywords
2. **Skill Overlap Extraction** — spaCy NER + custom skill dictionary identifies matched/missing skills
3. **Structured Features** — Text length, keyword density, and other engineered features

A gradient-boosted meta-learner (XGBoost) combines these signals to predict ATS compatibility scores, outperforming any single approach alone.

## 📊 Dataset

- **Name**: Resume-ATS Score Dataset v1 (English)
- **Source**: [Hugging Face — 0xnbk/resume-ats-score-v1-en](https://huggingface.co/datasets/0xnbk/resume-ats-score-v1-en)
- **Size**: ~6,400 resume–job description pairs (5,100 train / 1,300 validation)
- **Features**: Resume text, Job Description text, ATS compatibility score (18.3–90.7), Fit label (No Fit / Potential Fit / Good Fit)
- **Target Variable**: ATS compatibility score (continuous)

> **Note**: The dataset is automatically downloaded when you run the notebooks. No manual download needed.

## 🏗️ Project Structure

```
Project-Folder/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
│
├── notebooks/                   # Jupyter analysis notebook with all outputs
│   └── Capstone_Full_Pipeline.ipynb # End-to-end executed notebook (Parts 1-9)
│
├── src/                         # Reusable source modules
│   ├── __init__.py
│   ├── data_loader.py           # Dataset downloading & loading
│   ├── preprocessing.py         # Text cleaning & feature engineering
│   ├── feature_extraction.py    # TF-IDF, SBERT, skill extraction
│   ├── models.py                # Model training & evaluation utilities
│   └── utils.py                 # Helper functions
│
├── deployment/                  # Production Full-Stack Deployment
│   ├── backend/                 # FastAPI REST Microservice
│   │   ├── main.py              # Application entrypoint & static mounting
│   │   ├── matcher_service.py   # Hybrid NLP & 500+ Skill Ontology engine
│   │   ├── schemas.py           # Pydantic V2 request/response schemas
│   │   └── sample_data.py       # Global tech job postings & candidate personas
│   └── frontend/                # Modern Modular React UI
│       ├── index.html           # HTML5 shell
│       ├── app.js               # React 18 state & component architecture
│       └── styles.css           # Modern dark SaaS design system
│
├── models/                      # Saved trained models
│   └── (auto-generated .joblib files)
│
├── data/                        # Cached dataset files
│   └── (auto-downloaded)
│
├── outputs/                     # Generated figures and results
│   └── figures/                 # EDA and evaluation plots
│
└── paper/                       # IEEE LaTeX research paper
    ├── main.tex                 # LaTeX source
    ├── references.bib           # Bibliography
    ├── figures/                 # Paper figures
    └── main.pdf                 # Compiled PDF
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ahmad-Mustafa-Iqbal/Alture-AI.git
cd Alture-AI
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 3: Run the Notebook (Optional for inspection / re-training)
Open and run `notebooks/Capstone_Full_Pipeline.ipynb` in Jupyter Lab, VS Code, or Google Colab. All cells are pre-executed with visible outputs and visualizations.

### Step 4: Launch Production FastAPI Backend & React UI
```bash
# Launch the server (Serves both the REST API and the React Frontend on Port 8000)
python -m deployment.backend.main
```
Or with Uvicorn:
```bash
uvicorn deployment.backend.main:app --reload --port 8000
```
- 🌐 **Interactive Web UI**: Open [http://localhost:8000](http://localhost:8000) in your browser.
- 📖 **Interactive OpenAPI Swagger Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs).

## 📈 Model Performance & Results (Alture AI v2.0 Benchmark)

| Model | Architecture Type | MAE ↓ | RMSE ↓ | R² ↑ | Precision@Top25% ↑ | F1-Score ↑ | nDCG@10 ↑ |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Baseline 1: TF-IDF + Ridge | Lexical Linear | 17.55 | 21.40 | 0.265 | 0.674 | 0.611 | 0.670 |
| Baseline 2: TF-IDF + Random Forest | Lexical Ensemble | 20.53 | 24.07 | 0.070 | 0.444 | 0.090 | 0.490 |
| Baseline 3: SBERT + Ridge | Dense Semantic | 19.37 | 22.75 | 0.169 | 0.587 | 0.263 | 0.860 |
| **Proposed: Cross-Encoder + XGBoost** | **Hybrid Attention** | **17.15** | **20.79** | **0.306** | **0.672** | **0.524** | **0.943** |
| **Proposed: Cross-Encoder + LightGBM** | **Hybrid Fast Tree** | **17.17** | **20.63** | **0.316** | **0.688** | **0.529** | **0.905** |
| **Proposed: Cross-Encoder + CatBoost** | **Hybrid Categorical** | **18.54** | **21.84** | **0.234** | **0.632** | **0.378** | **0.964** |
| 🏆 **Proposed: Stacking Super-Ensemble** | **Multi-Modal Blend** | **17.32** | **20.72** | **0.311** | **0.709 (71%)** | **0.502** | **0.947 (95%)** |

*Note: Evaluated on out-of-sample holdout test split (1,275 samples).*

## 📏 Evaluation Metrics

- **MAE** (Mean Absolute Error) — Average prediction gap
- **RMSE** (Root Mean Squared Error) — Penalizes large errors
- **R² Score** — Variance explained by the model
- **Precision / Recall / F1-Score** — Classification performance on fit categories
- **nDCG@K** — Ranking quality for recommendation

## 🛠️ Technologies Used

- **Python 3.9+**
- **FastAPI & Uvicorn** — Production asynchronous REST API
- **React 18** — Component-driven interactive web interface
- **Pydantic V2** — Data validation and schemas
- **scikit-learn** — TF-IDF, linear models, ensemble metrics
- **sentence-transformers** — Sentence-BERT (`all-MiniLM-L6-v2`) & Cross-Encoders
- **spaCy** — Named entity recognition & skill extraction ontology
- **XGBoost / LightGBM / CatBoost** — Gradient boosted meta-learners
- **matplotlib / seaborn** — Statistical evaluation visualization
- **datasets** (HuggingFace) — Ingestion of resume-ATS corpus
- **matplotlib / seaborn / plotly** — Visualization
- **datasets** (HuggingFace) — Dataset loading

## 📝 Research Paper

The IEEE-format research paper is located in the `paper/` folder:
- `paper/main.tex` — LaTeX source file
- `paper/main.pdf` — Compiled PDF
- `paper/references.bib` — Bibliography

## 👤 Author

Ahmad — Internship Capstone Project (Week 7–8)

## 📄 License

This project is for educational purposes as part of an internship program.
