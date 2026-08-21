# Hybrid NLP-Based Job Recommendation and Resume–Job Matching System

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
├── deployment/                  # Gradio web application
│   ├── app.py                   # Main deployment app
│   └── model_utils.py           # Model loading & inference
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
git clone <repository-url>
cd Project-Folder
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 3: Run the Notebook (Optional for inspection / re-training)
Open and run `notebooks/Capstone_Full_Pipeline.ipynb` in Jupyter Lab, VS Code, or Google Colab. All cells are pre-executed with visible outputs and visualizations.

### Step 4: Run the Deployment App
```bash
python deployment/app.py
```
The Gradio app will launch at `http://localhost:7860`.

## 📈 Model Performance & Results

| Model | Type | MAE ↓ | RMSE ↓ | R² ↑ | Precision ↑ | F1-Score ↑ | nDCG@10 ↑ |
|-------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| TF-IDF + Ridge Regression | Baseline 1 | 18.27 | 22.27 | 0.204 | 0.626 | 0.529 | 0.481 |
| TF-IDF + Random Forest | Baseline 2 | 17.61 | 20.20 | 0.346 | 0.658 | 0.540 | 0.906 |
| SBERT + Ridge Regression | Baseline 3 | 18.78 | 22.14 | 0.213 | 0.641 | 0.434 | 0.847 |
| **Hybrid Model (XGBoost)** | **Proposed (Tuned)** | **18.48** | **21.83** | **0.236** | **0.676** | **0.434** | **0.898** |

*Note: Evaluated on independent test holdout (1,020 samples).*

## 📏 Evaluation Metrics

- **MAE** (Mean Absolute Error) — Average prediction gap
- **RMSE** (Root Mean Squared Error) — Penalizes large errors
- **R² Score** — Variance explained by the model
- **Precision / Recall / F1-Score** — Classification performance on fit categories
- **nDCG@K** — Ranking quality for recommendation

## 🛠️ Technologies Used

- **Python 3.9+**
- **scikit-learn** — ML models, TF-IDF, metrics
- **sentence-transformers** — Sentence-BERT embeddings
- **spaCy** — NLP, named entity recognition, skill extraction
- **XGBoost** — Gradient boosted meta-learner
- **Gradio** — Web deployment
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
