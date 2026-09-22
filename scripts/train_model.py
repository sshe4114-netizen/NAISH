from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["monthly_cash_flow_sar", "registration_age_months"]


def load_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.genfromtxt(path, delimiter=",", names=True)
    x = np.column_stack([data[name] for name in FEATURES]).astype(float)
    y = data["defaulted"].astype(int)
    return x, y


def train(dataset_path: Path, model_path: Path, metrics_path: Path) -> dict[str, float]:
    x, y = load_csv(dataset_path)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=113,
        stratify=y,
    )

    pipeline = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, random_state=113)),
        ]
    )
    pipeline.fit(x_train, y_train)

    coefficients = pipeline.named_steps["model"].coef_[0]
    if coefficients[0] > 0:
        raise RuntimeError("Training violated the required cash-flow monotonic direction")
    if coefficients[1] > 0:
        raise RuntimeError("Training produced an unexpected registration-age direction")

    probabilities = pipeline.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    metrics = {
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "brier_score": float(brier_score_loss(y_test, probabilities)),
        "test_rows": float(len(y_test)),
    }

    artifact = {
        "pipeline": pipeline,
        "features": FEATURES,
        "metrics": metrics,
        "decision_thresholds": {"auto_approve": 0.25, "manual_review": 0.55},
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return metrics


if __name__ == "__main__":
    metrics = train(
        Path("data/nasih_training.csv"),
        Path("artifacts/nasih_model.joblib"),
        Path("artifacts/metrics.json"),
    )
    print(json.dumps(metrics, indent=2))
