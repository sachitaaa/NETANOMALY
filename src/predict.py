
import joblib
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
MODEL_PATH = PROJECT_DIR / "models" / "random_forest.joblib"


def load_model():
    """Load the trained Random Forest model."""
    return joblib.load(MODEL_PATH)


def predict_record(model, record):
    """Predict whether one network-flow record is benign or an attack."""

    # Ensure the record has the same features and order used in training.
    expected_features = list(model.feature_names_in_)
    record = record.reindex(columns=expected_features)

    prediction = model.predict(record)[0]
    probabilities = model.predict_proba(record)[0]

    label = "Attack" if prediction == 1 else "Benign"
    attack_probability = probabilities[list(model.classes_).index(1)]

    return label, attack_probability



if __name__ == "__main__":
    from sklearn.metrics import classification_report, confusion_matrix

    model = load_model()

    dataset_path = DATA_DIR / "DDoS-Friday-no-metadata.parquet"
    df = pd.read_parquet(dataset_path)

    # Take a reproducible sample to keep evaluation manageable.
    sample = df.sample(
        n=min(10000, len(df)),
        random_state=42
    )

    X = sample.drop(columns=["Label"])
    y_actual = (sample["Label"] != "Benign").astype(int)

    # Use exactly the features expected by the saved model.
    X = X.reindex(columns=model.feature_names_in_)

    y_pred = model.predict(X)

    print("\n--- NetAnomaly Sample Evaluation ---")
    print("Records evaluated:", len(sample))

    print("\nClassification Report:")
    print(classification_report(
        y_actual,
        y_pred,
        labels=[0, 1],
        target_names=["Benign", "Attack"],
        digits=4,
        zero_division=0
    ))

    print("Confusion Matrix:")
    print(confusion_matrix(y_actual, y_pred, labels=[0, 1]))
