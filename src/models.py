"""
models.py — Model training, evaluation, and comparison utilities.

Provides standardized functions for training baseline and improved models,
computing metrics, and generating comparison reports.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
)
from sklearn.model_selection import cross_val_score, GridSearchCV
import joblib
import os
import time


# Metrics
def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute MAE, RMSE, and R² score for regression."""
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "R2": r2_score(y_true, y_pred),
    }


def compute_classification_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted"
) -> dict:
    """Compute Precision, Recall, and F1-Score for classification."""
    return {
        "Precision": precision_score(y_true, y_pred, average=average, zero_division=0),
        "Recall": recall_score(y_true, y_pred, average=average, zero_division=0),
        "F1": f1_score(y_true, y_pred, average=average, zero_division=0),
    }


def score_to_label(scores: np.ndarray, thresholds: tuple = (40, 65)) -> np.ndarray:
    """
    Convert continuous ATS scores to categorical labels.

    Thresholds:
      - score < 40  → 0 (No Fit)
      - 40 ≤ score < 65 → 1 (Potential Fit)
      - score ≥ 65 → 2 (Good Fit)
    """
    labels = np.zeros(len(scores), dtype=int)
    labels[scores >= thresholds[0]] = 1
    labels[scores >= thresholds[1]] = 2
    return labels


def compute_all_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                        label_thresholds: tuple = (40, 65)) -> dict:
    """Compute both regression and classification metrics."""
    reg_metrics = compute_regression_metrics(y_true, y_pred)

    # Convert to labels for classification metrics
    y_true_labels = score_to_label(y_true, label_thresholds)
    y_pred_labels = score_to_label(y_pred, label_thresholds)
    cls_metrics = compute_classification_metrics(y_true_labels, y_pred_labels)

    return {**reg_metrics, **cls_metrics}


def compute_ndcg_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int = 10) -> float:
    """
    Compute nDCG@K for ranking evaluation.

    This measures whether the top-K predicted matches are actually the
    best real matches — critical for recommendation quality.
    """
    # Get indices sorted by predicted score (descending)
    pred_order = np.argsort(-y_pred)[:k]
    ideal_order = np.argsort(-y_true)[:k]

    # DCG
    dcg = sum(y_true[pred_order[i]] / np.log2(i + 2) for i in range(min(k, len(pred_order))))
    # IDCG
    idcg = sum(y_true[ideal_order[i]] / np.log2(i + 2) for i in range(min(k, len(ideal_order))))

    if idcg == 0:
        return 0.0
    return dcg / idcg


# Model Training
class ModelTrainer:
    """
    Unified interface for training, evaluating, and saving models.
    """

    def __init__(self, model, model_name: str, random_state: int = 42):
        self.model = model
        self.model_name = model_name
        self.random_state = random_state
        self.train_time = None
        self.metrics = {}

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> "ModelTrainer":
        """Train the model and record training time."""
        print(f"\n  [TRAINING] {self.model_name} ...")
        start = time.time()
        self.model.fit(X_train, y_train)
        self.train_time = time.time() - start
        print(f"  [DONE] Training time: {self.train_time:.2f}s")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions."""
        return self.model.predict(X)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """Evaluate on test data and store metrics."""
        y_pred = self.predict(X_test)
        self.metrics = compute_all_metrics(y_test, y_pred)
        self.metrics["nDCG@10"] = compute_ndcg_at_k(y_test, y_pred, k=10)
        self.metrics["Train Time (s)"] = round(self.train_time, 2) if self.train_time else None

        print(f"\n  {'─' * 50}")
        print(f"  EVALUATION: {self.model_name}")
        print(f"  {'─' * 50}")
        for k, v in self.metrics.items():
            if isinstance(v, float):
                print(f"    {k:20s}: {v:.4f}")
            else:
                print(f"    {k:20s}: {v}")
        return self.metrics

    def cross_validate(self, X: np.ndarray, y: np.ndarray,
                       cv: int = 5, scoring: str = "neg_mean_absolute_error") -> dict:
        """Run cross-validation and return mean/std scores."""
        print(f"\n  [CV] Running {cv}-fold cross-validation for {self.model_name} ...")
        scores = cross_val_score(self.model, X, y, cv=cv, scoring=scoring, n_jobs=-1)

        if "neg_" in scoring:
            scores = -scores
            metric_name = scoring.replace("neg_", "")
        else:
            metric_name = scoring

        cv_results = {
            f"CV_{metric_name}_mean": scores.mean(),
            f"CV_{metric_name}_std": scores.std(),
        }
        print(f"  [CV] {metric_name}: {scores.mean():.4f} ± {scores.std():.4f}")
        return cv_results

    def save(self, directory: str = "models") -> str:
        """Save trained model to disk."""
        os.makedirs(directory, exist_ok=True)
        filename = f"{self.model_name.lower().replace(' ', '_')}.joblib"
        filepath = os.path.join(directory, filename)
        joblib.dump(self.model, filepath)
        print(f"  [INFO] Model saved to {filepath}")
        return filepath

    @classmethod
    def load(cls, filepath: str, model_name: str = "Loaded Model") -> "ModelTrainer":
        """Load a trained model from disk."""
        model = joblib.load(filepath)
        trainer = cls(model, model_name)
        return trainer


# Model Comparison
def compare_models(results: dict) -> pd.DataFrame:
    """
    Create a comparison DataFrame from multiple model results.

    Parameters
    ----------
    results : dict[str, dict] — model_name → metrics_dict

    Returns
    -------
    pd.DataFrame with models as rows and metrics as columns.
    """
    df = pd.DataFrame(results).T
    df.index.name = "Model"

    # Reorder columns for readability
    metric_order = ["MAE", "RMSE", "R2", "Precision", "Recall", "F1", "nDCG@10", "Train Time (s)"]
    cols = [c for c in metric_order if c in df.columns]
    df = df[cols]

    # Round values
    for col in df.columns:
        if df[col].dtype in [np.float64, float]:
            df[col] = df[col].round(4)

    return df


def print_comparison_table(comparison_df: pd.DataFrame) -> None:
    """Pretty-print the model comparison table."""
    print("\n" + "=" * 90)
    print("MODEL COMPARISON TABLE")
    print("=" * 90)
    try:
        from tabulate import tabulate
        print(tabulate(comparison_df, headers="keys", tablefmt="grid", floatfmt=".4f"))
    except ImportError:
        print(comparison_df.to_string())
    print("=" * 90)


# Hyperparameter Tuning
def tune_hyperparameters(model, param_grid: dict, X_train: np.ndarray,
                         y_train: np.ndarray, cv: int = 5,
                         scoring: str = "neg_mean_absolute_error",
                         n_jobs: int = -1) -> tuple:
    """
    Run GridSearchCV for hyperparameter tuning.

    Returns
    -------
    (best_model, best_params, cv_results_df)
    """
    print(f"\n  [TUNING] GridSearchCV with {cv}-fold CV ...")
    print(f"  [TUNING] Parameter grid: {param_grid}")

    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=cv,
        scoring=scoring,
        n_jobs=n_jobs,
        verbose=1,
        refit=True,
    )
    grid_search.fit(X_train, y_train)

    print(f"\n  [TUNING] Best params: {grid_search.best_params_}")
    print(f"  [TUNING] Best score:  {-grid_search.best_score_:.4f}")

    results_df = pd.DataFrame(grid_search.cv_results_)
    return grid_search.best_estimator_, grid_search.best_params_, results_df


if __name__ == "__main__":
    # Quick test
    from sklearn.datasets import make_regression
    X, y = make_regression(n_samples=100, n_features=10, random_state=42)
    trainer = ModelTrainer(Ridge(random_state=42), "Test Ridge")
    trainer.train(X[:80], y[:80])
    trainer.evaluate(X[80:], y[80:])
