
import joblib
import pandas as pd
from pathlib import Path
from sklearn.metrics import confusion_matrix

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
MODEL_PATH = PROJECT_DIR / "models" / "random_forest.joblib"


def main():
    # Load the saved baseline model.
    model = joblib.load(MODEL_PATH)

    # Load Friday DDoS traffic.
    dataset_path = DATA_DIR / "DDoS-Friday-no-metadata.parquet"
    df = pd.read_parquet(dataset_path)

    # Use the same reproducible 10,000-record sample as predict.py.
    sample = df.sample(n=min(10000, len(df)), random_state=42)

    X = sample.drop(columns=["Label"])
    y_actual = (sample["Label"] != "Benign").astype(int)

    # Match the model's expected feature columns and order.
    X = X.reindex(columns=model.feature_names_in_)

    # Get attack probabilities once, then compare thresholds.
    attack_column = list(model.classes_).index(1)
    attack_probabilities = model.predict_proba(X)[:, attack_column]

    print("\n--- NetAnomaly Threshold Experiment ---")
    print("Records evaluated:", len(sample))
    print("Actual attacks:", int(y_actual.sum()))
    print("Actual benign records:", int((y_actual == 0).sum()))

    for threshold in [0.10, 0.20, 0.30, 0.40, 0.50]:
        y_pred = (attack_probabilities >= threshold).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_actual, y_pred, labels=[0, 1]
        ).ravel()

        recall = tp / (tp + fn) if (tp + fn) else 0
        precision = tp / (tp + fp) if (tp + fp) else 0

        print(f"\nThreshold: {threshold:.2f}")
        print(f"Attacks detected: {tp}/{tp + fn}")
        print(f"Attacks missed: {fn}")
        print(f"False alarms: {fp}")
        print(f"Attack recall: {recall:.2%}")
        print(f"Attack precision: {precision:.2%}")


if __name__ == "__main__":
    main()
