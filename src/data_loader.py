"""
data_loader.py — Dataset downloading and loading utilities.

Loads the Resume-ATS Score Dataset v1 (English) from Hugging Face,
parses the combined text field into separate resume and job description columns,
and provides clean DataFrames for downstream use.
"""

import os
import re
import pandas as pd
from datasets import load_dataset


# Constants
DATASET_NAME = "0xnbk/resume-ats-score-v1-en"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


# Core loading function
def load_raw_dataset(cache_dir: str | None = None) -> dict:
    """
    Download the dataset from Hugging Face and return train/validation splits.

    Returns
    -------
    dict with keys 'train' and 'validation', each a pandas DataFrame
    with columns: text, ats_score, original_label.
    """
    cache = cache_dir or DATA_DIR
    os.makedirs(cache, exist_ok=True)

    print(f"[INFO] Loading dataset '{DATASET_NAME}' from Hugging Face ...")
    ds = load_dataset(DATASET_NAME, cache_dir=cache)

    splits = {}
    for split_name in ("train", "validation"):
        df = ds[split_name].to_pandas()
        print(f"  > {split_name}: {len(df):,} rows, columns = {list(df.columns)}")
        splits[split_name] = df

    return splits


# Text parsing helpers
def _extract_resume_and_jd(text: str) -> tuple:
    """
    Parse the combined 'text' field to separate resume and job description.

    The dataset stores both documents in a single text column. This function
    uses heuristic patterns to split them.

    Returns
    -------
    (resume_text, job_description_text)  -- both stripped strings.
    """
    text = str(text)

    # Primary separator: The dataset uses ' SEP ' to separate resume from JD
    # This separator is present in 100% of the dataset rows
    if " SEP " in text:
        parts = text.split(" SEP ", maxsplit=1)
        resume = parts[0].strip()
        jd = parts[1].strip()
        if len(resume) > 10 and len(jd) > 10:
            return resume, jd

    # Fallback 1: Try common JD header patterns
    separators = [
        r"(?i)job\s*description\s*[:\-]",
        r"(?i)position\s*description\s*[:\-]",
        r"(?i)role\s*description\s*[:\-]",
    ]

    for sep_pattern in separators:
        match = re.search(sep_pattern, text)
        if match:
            resume = text[: match.start()].strip()
            jd = text[match.start() :].strip()
            if len(resume) > 50 and len(jd) > 50:
                return resume, jd

    # Fallback 2: split roughly in half
    mid = len(text) // 2
    return text[:mid].strip(), text[mid:].strip()


def parse_text_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'resume_text' and 'jd_text' columns by parsing the 'text' column.

    Parameters
    ----------
    df : DataFrame with a 'text' column.

    Returns
    -------
    DataFrame with added 'resume_text' and 'jd_text' columns.
    """
    print("[INFO] Parsing 'text' column into resume_text and jd_text ...")
    parsed = df["text"].apply(_extract_resume_and_jd)
    df = df.copy()
    df["resume_text"] = parsed.apply(lambda x: x[0])
    df["jd_text"] = parsed.apply(lambda x: x[1])
    print(f"  > Done. Average resume length: {df['resume_text'].str.len().mean():.0f} chars")
    print(f"  > Done. Average JD length:     {df['jd_text'].str.len().mean():.0f} chars")
    return df


# Convenience function: load and parse in one call
def load_and_parse_dataset(cache_dir: str | None = None) -> dict:
    """
    Load dataset from Hugging Face and parse text into resume + JD.

    Returns
    -------
    dict with keys 'train' and 'validation', each a DataFrame with columns:
      text, ats_score, original_label, resume_text, jd_text.
    """
    splits = load_raw_dataset(cache_dir)
    for split_name in splits:
        splits[split_name] = parse_text_column(splits[split_name])
    return splits


# Dataset summary
def print_dataset_summary(splits: dict) -> None:
    """Print a formatted summary of the loaded dataset."""
    print("\n" + "=" * 70)
    print("DATASET SUMMARY: Resume-ATS Score Dataset v1 (English)")
    print("=" * 70)
    print(f"  Source       : Hugging Face — {DATASET_NAME}")
    print(f"  License      : Apache 2.0")
    print(f"  Task         : ATS compatibility score prediction")
    print()

    for name, df in splits.items():
        print(f"  Split '{name}':")
        print(f"    Rows       : {len(df):,}")
        print(f"    Columns    : {list(df.columns)}")
        print(f"    Score range: {df['ats_score'].min():.1f} – {df['ats_score'].max():.1f}")
        print(f"    Labels     : {df['original_label'].value_counts().to_dict()}")
        print()

    total = sum(len(df) for df in splits.values())
    print(f"  Total samples: {total:,}")
    print("=" * 70)


if __name__ == "__main__":
    splits = load_and_parse_dataset()
    print_dataset_summary(splits)
