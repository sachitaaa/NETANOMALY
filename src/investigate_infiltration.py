
import pandas as pd
import joblib
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
MODEL_PATH = PROJECT_DIR / "models" / "random_forest_friday_experiment.joblib"

if __name__ == "__main__":
    print("Loading model and Thursday data...")
    model = joblib.load(MODEL_PATH)

    df = pd.read_parquet(
        DATA_DIR / "Infiltration-Thursday-no-metadata.parquet"
    )

    X = df.drop(columns=["Label"])
    X = X[model.feature_names_in_]
    y_true = (df["Label"] != "Benign").astype(int)

    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= 0.50).astype(int)

    groups = {
        "Correctly classified benign": (y_true == 0) & (predictions == 0),
        "False positives": (y_true == 0) & (predictions == 1),
        "Missed Infiltration attacks": (y_true == 1) & (predictions == 0),
    }

    print("\nAttack probability statistics:\n")

    for name, mask in groups.items():
        scores = probabilities[mask]

        print(f"\n{name}:")
        print(f"Count: {len(scores)}")
        print(f"Mean probability: {scores.mean():.4f}")
        print(f"Median probability: {__import__('numpy').median(scores):.4f}")
        print(f"Minimum probability: {scores.min():.4f}")
        print(f"Maximum probability: {scores.max():.4f}")
