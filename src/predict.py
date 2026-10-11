
import joblib
import pandas as pd
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
MODEL_PATH = PROJECT_DIR / "models" / "random_forest.joblib"


def load_model():
    """Load the trained Random Forest model."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}\n"
            "Run python src/train_model.py first."
        )

    return joblib.load(MODEL_PATH)


def predict_record(model, record):
    """Predict whether one network-flow record is benign or an attack."""

    expected_features = list(model.feature_names_in_)

    # Check whether the input contains all required features.
    missing_features = set(expected_features) - set(record.columns)

    if missing_features:
        raise ValueError(
            f"Missing required features: {sorted(missing_features)}"
        )

    # Ensure features appear in the same order as during training.
    record = record.reindex(columns=expected_features)

    # Make the prediction.
    prediction = model.predict(record)[0]
    probabilities = model.predict_proba(record)[0]

    label = "Attack" if prediction == 1 else "Benign"
    attack_probability = probabilities[list(model.classes_).index(1)]

    return label, attack_probability


def evaluate_sample(model):
    """Evaluate the model on a reproducible sample of Friday traffic."""

    dataset_path = DATA_DIR / "DDoS-Friday-no-metadata.parquet"

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    df = pd.read_parquet(dataset_path)

    # Select a reproducible sample to keep evaluation manageable.
    sample = df.sample(
        n=min(10000, len(df)),
        random_state=42
    )

    X = sample.drop(columns=["Label"])
    y_actual = (sample["Label"] != "Benign").astype(int)

    # Align feature names and order with the saved model.
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




if __name__ == "__main__":
    model = load_model()

    # First, evaluate the model on a sample of Friday traffic.
    evaluate_sample(model)

    # Load Friday traffic for single-record prediction.
    dataset_path = DATA_DIR / "DDoS-Friday-no-metadata.parquet"
    df = pd.read_parquet(dataset_path)

    # Ask the user which record to predict.
    row_number = int(
        input(f"Enter a row number (0 to {len(df) - 1}): ")
    )

    # Validate the selected row number.
    if row_number < 0 or row_number >= len(df):
        raise ValueError("Row number is out of range.")

    # Select one record, excluding its actual label from the input.
    record = df.drop(columns=["Label"]).iloc[[row_number]]

    # Predict and display the result.
    predicted_label, attack_probability = predict_record(model, record)

    print("\n--- Single Record Prediction ---")
    print("Predicted label:", predicted_label)
    print(f"Attack probability: {attack_probability:.2%}")
    print("Actual label:", df["Label"].iloc[row_number])

    