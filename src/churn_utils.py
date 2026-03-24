from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


FREQUENCY_MAP: Dict[str, int] = {
    "Monthly": 12,
    "Quarterly": 4,
    "Annual": 1,
    "Semi-Annual": 2,
    "Bi-Weekly": 26,
    "Weekly": 52,
    "Once": 1,
}


def find_dataset_path(filename: str = "Insurance Churn Dataset.xlsx") -> Path:
    candidates = [
        Path.cwd() / "data" / filename,
        Path.cwd().parent / "data" / filename,
        Path("/mnt/data") / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        f"Could not locate {filename}. Put the file in ./data or update the notebook path."
    )


def load_data(path: str | Path | None = None) -> pd.DataFrame:
    dataset_path = Path(path) if path else find_dataset_path()
    df = pd.read_excel(dataset_path)
    df["churn_reason"] = df["churn_reason"].fillna("No Churn")
    df["annual_premium"] = df["premium_amount"] * df["premium_frequency"].map(FREQUENCY_MAP)
    df["clv_proxy"] = df["annual_premium"] * df["tenure_year"]
    return df


def build_feature_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, list[str]]:
    df_model = pd.get_dummies(
        df.copy(),
        columns=["channel", "health_status", "policy_term"],
        drop_first=True,
    )
    feature_cols = [
        "issue_age",
        "tenure_year",
        "premium_amount",
        "satisfaction_score",
        "number_of_dependents",
        "clv_proxy",
    ]
    feature_cols += [
        c for c in df_model.columns
        if any(prefix in c for prefix in ["channel_", "health_status_", "policy_term_"])
    ]
    X = df_model[feature_cols]
    y = df_model["churn?"]
    return X, y, feature_cols


def train_balanced_logistic_regression(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
):
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=random_state,
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(
        solver="liblinear",
        class_weight="balanced",
        random_state=random_state,
    )
    model.fit(X_train_scaled, y_train)

    return {
        "model": model,
        "scaler": scaler,
        "X_train": X_train,
        "X_test": X_test,
        "X_train_scaled": X_train_scaled,
        "X_test_scaled": X_test_scaled,
        "y_train": y_train,
        "y_test": y_test,
        "y_prob": model.predict_proba(X_test_scaled)[:, 1],
    }


def evaluate_threshold(y_true: pd.Series, y_prob: np.ndarray, threshold: float) -> dict:
    y_pred = (y_prob > threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "threshold": threshold,
        "flagged": int(y_pred.sum()),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "auc_roc": float(roc_auc_score(y_true, y_prob)),
        "average_precision": float(average_precision_score(y_true, y_prob)),
        "precision": float(precision),
        "recall": float(recall),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }


def threshold_table(y_true: pd.Series, y_prob: np.ndarray, thresholds: Iterable[float]) -> pd.DataFrame:
    rows = [evaluate_threshold(y_true, y_prob, threshold) for threshold in thresholds]
    return pd.DataFrame(rows)


def coefficient_table(model: LogisticRegression, feature_names: list[str]) -> pd.DataFrame:
    coeffs = pd.DataFrame({
        "feature": feature_names,
        "coefficient": model.coef_[0],
    })
    coeffs["abs_coefficient"] = coeffs["coefficient"].abs()
    return coeffs.sort_values("abs_coefficient", ascending=False)


def gains_table(y_true: pd.Series, y_prob: np.ndarray) -> pd.DataFrame:
    gains = pd.DataFrame({
        "actual_churn": y_true.to_numpy(),
        "risk_score": y_prob,
    }).sort_values("risk_score", ascending=False).reset_index(drop=True)
    gains["cum_customer_pct"] = (np.arange(1, len(gains) + 1) / len(gains))
    gains["cum_churners"] = gains["actual_churn"].cumsum()
    gains["cum_churner_pct"] = gains["cum_churners"] / gains["actual_churn"].sum()
    return gains
