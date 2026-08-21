"""
preprocessing.py — Text cleaning and feature engineering pipeline.

Every preprocessing step is justified and documented, as required
by the capstone project rubric (Part 4).
"""

import re
import numpy as np
import pandas as pd


# Text Cleaning Functions
def clean_text(text: str) -> str:
    """
    Clean raw text for NLP processing.

    Steps & Justifications:
    1. Lowercase: Ensures "Python" and "python" are treated equally.
    2. Remove URLs: URLs add noise without semantic value for matching.
    3. Remove email addresses: PII removal + noise reduction.
    4. Remove phone numbers: PII removal + noise reduction.
    5. Remove special characters: Keep only alphanumeric, spaces, and basic punctuation.
    6. Normalize whitespace: Consistent formatting for tokenization.
    """
    if not isinstance(text, str) or len(text) == 0:
        return ""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Step 3: Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", " ", text)

    # Step 4: Remove phone numbers
    text = re.sub(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}", " ", text)

    # Step 5: Remove special characters (keep alphanumeric, spaces, basic punctuation)
    text = re.sub(r"[^a-z0-9\s\.\,\;\:\-\/\(\)\+\#]", " ", text)

    # Step 6: Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_text_column(df: pd.DataFrame, col: str, new_col: str | None = None) -> pd.DataFrame:
    """Apply text cleaning to a DataFrame column."""
    target = new_col or f"{col}_clean"
    df = df.copy()
    df[target] = df[col].apply(clean_text)
    empty_count = (df[target].str.len() == 0).sum()
    if empty_count > 0:
        print(f"  [WARN] {empty_count} empty strings after cleaning column '{col}'")
    return df


# Missing Value Handling
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check and handle missing values.

    Justification: Missing text values would cause errors in TF-IDF and SBERT
    encoding. Missing scores would corrupt training labels.
    """
    df = df.copy()
    missing = df.isnull().sum()
    total_missing = missing.sum()

    if total_missing > 0:
        print(f"  [INFO] Found {total_missing} missing values:")
        print(missing[missing > 0])

        # Fill missing text with empty string (will be flagged by length features)
        text_cols = [c for c in df.columns if "text" in c.lower()]
        for col in text_cols:
            df[col] = df[col].fillna("")

        # Drop rows with missing scores (critical for training)
        if "ats_score" in df.columns:
            before = len(df)
            df = df.dropna(subset=["ats_score"])
            dropped = before - len(df)
            if dropped > 0:
                print(f"  [INFO] Dropped {dropped} rows with missing ATS scores")
    else:
        print("  [INFO] No missing values found.")

    return df


# Label Encoding
LABEL_MAP = {"No Fit": 0, "Potential Fit": 1, "Good Fit": 2}
LABEL_MAP_INV = {v: k for k, v in LABEL_MAP.items()}


def encode_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map original_label to numeric categories.

    Justification: Classification models require numeric targets.
    The ordinal encoding (0 < 1 < 2) preserves the natural ordering
    of fit quality.
    """
    df = df.copy()
    if "original_label" in df.columns:
        df["label_encoded"] = df["original_label"].map(LABEL_MAP)
        unmapped = df["label_encoded"].isnull().sum()
        if unmapped > 0:
            print(f"  [WARN] {unmapped} rows have unmapped labels")
            # Map any unknown labels to the most common class
            mode = df["label_encoded"].mode()[0]
            df["label_encoded"] = df["label_encoded"].fillna(mode)
        df["label_encoded"] = df["label_encoded"].astype(int)
        print(f"  [INFO] Labels encoded: {LABEL_MAP}")
    return df


# Feature Engineering
def add_text_length_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add text-length-based features.

    Justification: Text length correlates with the level of detail in a resume
    or job description. A very short resume may indicate missing information,
    while a very long JD may indicate a senior role with many requirements.
    The length ratio captures whether the resume is proportionally detailed
    relative to the job description.
    """
    df = df.copy()

    # Character counts
    if "resume_text" in df.columns:
        df["resume_char_len"] = df["resume_text"].str.len()
        df["resume_word_count"] = df["resume_text"].str.split().str.len()

    if "jd_text" in df.columns:
        df["jd_char_len"] = df["jd_text"].str.len()
        df["jd_word_count"] = df["jd_text"].str.split().str.len()

    # Length ratio
    if "resume_char_len" in df.columns and "jd_char_len" in df.columns:
        df["length_ratio"] = df["resume_char_len"] / (df["jd_char_len"] + 1)  # +1 to avoid division by zero

    print("  [INFO] Added text length features: resume_char_len, resume_word_count, "
          "jd_char_len, jd_word_count, length_ratio")
    return df


def add_keyword_density_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add keyword density features.

    Justification: The proportion of JD keywords that appear in the resume
    is a strong signal for keyword-based ATS matching. This creates a
    simple but effective overlap metric.
    """
    df = df.copy()

    def keyword_overlap(row):
        if "resume_text" not in row or "jd_text" not in row:
            return 0.0
        resume_words = set(str(row["resume_text"]).lower().split())
        jd_words = set(str(row["jd_text"]).lower().split())
        if len(jd_words) == 0:
            return 0.0
        overlap = resume_words.intersection(jd_words)
        return len(overlap) / len(jd_words)

    df["keyword_overlap_ratio"] = df.apply(keyword_overlap, axis=1)
    print("  [INFO] Added keyword_overlap_ratio feature")
    return df


# Full Preprocessing Pipeline
def run_preprocessing_pipeline(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Run the complete preprocessing pipeline.

    Steps:
    1. Handle missing values
    2. Clean text columns
    3. Encode labels
    4. Add text length features
    5. Add keyword density features

    Each step is justified in its respective function docstring.
    """
    if verbose:
        print("\n" + "=" * 60)
        print("PREPROCESSING PIPELINE")
        print("=" * 60)

    # Step 1: Handle missing values
    if verbose:
        print("\n[Step 1] Handling missing values ...")
    df = handle_missing_values(df)

    # Step 2: Clean text
    if verbose:
        print("\n[Step 2] Cleaning text columns ...")
    if "resume_text" in df.columns:
        df = clean_text_column(df, "resume_text", "resume_clean")
    if "jd_text" in df.columns:
        df = clean_text_column(df, "jd_text", "jd_clean")

    # Step 3: Encode labels
    if verbose:
        print("\n[Step 3] Encoding labels ...")
    df = encode_labels(df)

    # Step 4: Text length features
    if verbose:
        print("\n[Step 4] Adding text length features ...")
    df = add_text_length_features(df)

    # Step 5: Keyword density features
    if verbose:
        print("\n[Step 5] Adding keyword density features ...")
    df = add_keyword_density_features(df)

    if verbose:
        print("\n" + "=" * 60)
        print(f"PREPROCESSING COMPLETE — {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        print("=" * 60)

    return df


if __name__ == "__main__":
    # Quick test
    test_df = pd.DataFrame({
        "text": ["Sample resume text ... Job Description: Sample JD text"],
        "resume_text": ["Sample resume text with Python and machine learning"],
        "jd_text": ["Looking for Python developer with machine learning experience"],
        "ats_score": [75.5],
        "original_label": ["Good Fit"],
    })
    result = run_preprocessing_pipeline(test_df)
    print(result.head())
