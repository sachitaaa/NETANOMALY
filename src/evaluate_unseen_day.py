import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
MODEL_PATH = PROJECT_DIR / "models" / "random_forest_friday_experiment.joblib"


def load_dataset(filename):
    """Load a Parquet dataset from the data directory."""
    file_path = DATA_DIR / filename
    return pd.read_parquet(file_path)


def evaluate_predictions(y_true, y_pred, title):
    """Print classification metrics and a confusion matrix."""
    print(f"\n{title} Classification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=[0, 1],
            target_names=["Benign", "Attack"],
            digits=4,
            zero_division=0
        )
    )

    print(f"\n{title} Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred, labels=[0, 1]))


if __name__ == "__main__":

    # 1. Load the previously trained model
    print("Loading trained model...")
    model = joblib.load(MODEL_PATH)

    # 2. Load Thursday Infiltration data
    print("\nLoading Thursday Infiltration data...")
    df_thursday = load_dataset(
        "Infiltration-Thursday-no-metadata.parquet"
    )

    # 3. Separate features and target
    X_thursday = df_thursday.drop(columns=["Label"])
    y_thursday = (
        df_thursday["Label"] != "Benign"
    ).astype(int)

    # Match the model's expected feature names and order
    X_thursday = X_thursday[model.feature_names_in_]

    print("\nThursday label distribution:")
    print(df_thursday["Label"].value_counts())

    # 4. Get attack probabilities
    print("\nEvaluating on unseen Thursday traffic...")
    attack_probabilities = model.predict_proba(X_thursday)[:, 1]

    # Inspect probabilities for actual Infiltration records
    infiltration_probabilities = attack_probabilities[
        y_thursday.to_numpy() == 1
    ]

    print("\nAttack probabilities for Infiltration records:")
    print(pd.Series(infiltration_probabilities).describe())

    # 5. Evaluate using the default threshold of 0.50
    y_pred_default = (attack_probabilities >= 0.50).astype(int)

    evaluate_predictions(
        y_thursday,
        y_pred_default,
        "Thursday - Default threshold (0.50)"
    )

    # 6. Exploratory evaluation using a threshold of 0.10
    # This threshold is for investigation, not final model selection.
    threshold = 0.10
    y_pred_adjusted = (
        attack_probabilities >= threshold
    ).astype(int)

    evaluate_predictions(
        y_thursday,
        y_pred_adjusted,
        "Thursday - Exploratory threshold (0.10)"
    )
