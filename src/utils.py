"""
utils.py — Helper functions for reproducibility, plotting, and I/O.
"""

import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Reproducibility
RANDOM_STATE = 42


def set_seed(seed: int = RANDOM_STATE) -> None:
    """Set random seed for reproducibility across all libraries."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
    print(f"[INFO] Random seed set to {seed}")


# Plotting Configuration
def setup_plotting_style() -> None:
    """Configure matplotlib/seaborn for publication-quality plots."""
    import matplotlib
    matplotlib.use("Agg")
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "figure.dpi": 100,
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 16,
        "axes.grid": True,
        "grid.alpha": 0.3,
    })
    sns.set_theme(style="whitegrid", palette="deep")
    print("[INFO] Plotting style configured.")


# Output Directory Management
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
FIGURES_DIR = os.path.join(OUTPUTS_DIR, "figures")


def ensure_output_dirs() -> None:
    """Create output directories if they don't exist."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "models"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"), exist_ok=True)


def save_figure(fig: plt.Figure, filename: str, dpi: int = 150) -> str:
    """Save a figure to the outputs/figures directory."""
    ensure_output_dirs()
    filepath = os.path.join(FIGURES_DIR, filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"  [INFO] Figure saved: {filepath}")
    return filepath


# Common Visualization Functions
def plot_actual_vs_predicted(y_true, y_pred, model_name: str = "Model",
                              save_name: str | None = None) -> plt.Figure:
    """Scatter plot of actual vs. predicted ATS scores."""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(y_true, y_pred, alpha=0.4, s=20, edgecolors="white", linewidth=0.5)
    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))
    ax.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2, label="Perfect prediction")
    ax.set_xlabel("Actual ATS Score")
    ax.set_ylabel("Predicted ATS Score")
    ax.set_title(f"Actual vs. Predicted — {model_name}")
    ax.legend()
    plt.tight_layout()

    if save_name:
        save_figure(fig, save_name)
    return fig


def plot_residuals(y_true, y_pred, model_name: str = "Model",
                   save_name: str | None = None) -> plt.Figure:
    """Plot residual distribution."""
    residuals = np.array(y_true) - np.array(y_pred)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Residual distribution
    axes[0].hist(residuals, bins=50, edgecolor="black", alpha=0.7, color="steelblue")
    axes[0].axvline(0, color="red", linestyle="--", linewidth=2)
    axes[0].set_xlabel("Residual (Actual - Predicted)")
    axes[0].set_ylabel("Frequency")
    axes[0].set_title(f"Residual Distribution — {model_name}")

    # Residual vs. Predicted
    axes[1].scatter(y_pred, residuals, alpha=0.4, s=20)
    axes[1].axhline(0, color="red", linestyle="--", linewidth=2)
    axes[1].set_xlabel("Predicted ATS Score")
    axes[1].set_ylabel("Residual")
    axes[1].set_title(f"Residual vs. Predicted — {model_name}")

    plt.tight_layout()
    if save_name:
        save_figure(fig, save_name)
    return fig


def plot_confusion_matrix(y_true, y_pred, labels: list | None = None,
                           model_name: str = "Model",
                           save_name: str | None = None) -> plt.Figure:
    """Plot confusion matrix for classification."""
    if labels is None:
        labels = ["No Fit", "Potential Fit", "Good Fit"]

    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels,
                yticklabels=labels, ax=ax, cbar_kws={"label": "Count"})
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix — {model_name}")
    plt.tight_layout()

    if save_name:
        save_figure(fig, save_name)
    return fig


def plot_model_comparison(comparison_df: pd.DataFrame,
                           metric: str = "MAE",
                           save_name: str | None = None) -> plt.Figure:
    """Bar chart comparing models on a specific metric."""
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("viridis", n_colors=len(comparison_df))

    bars = ax.bar(comparison_df.index, comparison_df[metric], color=colors, edgecolor="black")

    # Add value labels on bars
    for bar, val in zip(bars, comparison_df[metric]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01 * max(comparison_df[metric]),
                f"{val:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=10)

    ax.set_xlabel("Model")
    ax.set_ylabel(metric)
    ax.set_title(f"Model Comparison — {metric}")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()

    if save_name:
        save_figure(fig, save_name)
    return fig


# Data Saving / Loading
def save_dataframe(df: pd.DataFrame, filename: str) -> str:
    """Save DataFrame to outputs directory."""
    ensure_output_dirs()
    filepath = os.path.join(OUTPUTS_DIR, filename)
    df.to_csv(filepath, index=True)
    print(f"  [INFO] DataFrame saved: {filepath}")
    return filepath


def load_dataframe(filename: str) -> pd.DataFrame:
    """Load DataFrame from outputs directory."""
    filepath = os.path.join(OUTPUTS_DIR, filename)
    return pd.read_csv(filepath, index_col=0)


# Environment Info
def print_environment_info() -> None:
    """Print versions of key libraries for reproducibility."""
    import sys
    import sklearn
    print("\n" + "=" * 50)
    print("ENVIRONMENT INFO")
    print("=" * 50)
    print(f"  Python       : {sys.version}")
    print(f"  NumPy        : {np.__version__}")
    print(f"  Pandas       : {pd.__version__}")
    print(f"  scikit-learn : {sklearn.__version__}")
    try:
        import sentence_transformers
        print(f"  sentence-transformers : {sentence_transformers.__version__}")
    except ImportError:
        print("  sentence-transformers : not installed")
    try:
        import xgboost
        print(f"  XGBoost      : {xgboost.__version__}")
    except ImportError:
        print("  XGBoost      : not installed")
    try:
        import torch
        print(f"  PyTorch      : {torch.__version__}")
        print(f"  CUDA         : {'Available' if torch.cuda.is_available() else 'Not available'}")
    except ImportError:
        print("  PyTorch      : not installed")
    print("=" * 50)
