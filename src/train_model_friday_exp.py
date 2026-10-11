import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"


def load_dataset(filename):
    """Load one Parquet dataset from the data directory."""
    file_path = DATA_DIR / filename
    return pd.read_parquet(file_path)


def prepare_data(df):
    """Separate input features from the binary target."""
    X = df.drop(columns=["Label"])
    y = (df["Label"] != "Benign").astype(int)
    return X, y


def evaluate_model(model, X_test, y_test, title):
    """Print classification metrics and the confusion matrix."""
    predictions = model.predict(X_test)

    print(f"\n{title} Classification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=["Benign", "Attack"],
            digits=4,
            zero_division=0
        )
    )

    print(f"\n{title} Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))


if __name__ == "__main__":

    # 1. Load Tuesday and Wednesday data
    print("Loading Tuesday and Wednesday datasets...")

    df_tuesday = load_dataset("Bruteforce-Tuesday-no-metadata.parquet")
    df_wednesday = load_dataset("DoS-Wednesday-no-metadata.parquet")

    df_combined = pd.concat(
        [df_tuesday, df_wednesday],
        ignore_index=True
    )

    X, y = prepare_data(df_combined)

    # 2. Split Tuesday and Wednesday data
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # 3. Load and split Friday data
    print("\nLoading Friday DDoS dataset...")

    df_friday = load_dataset("DDoS-Friday-no-metadata.parquet")
    X_friday, y_friday = prepare_data(df_friday)

    X_friday_train, X_friday_test, y_friday_train, y_friday_test = (
        train_test_split(
            X_friday,
            y_friday,
            test_size=0.2,
            random_state=42,
            stratify=y_friday
        )
    )

    print("\nTuesday + Wednesday training samples:", len(X_train))
    print("Tuesday + Wednesday test samples:", len(X_test))
    print("Friday training samples:", len(X_friday_train))
    print("Friday test samples:", len(X_friday_test))

    # 4. Combine training data only
    X_train_all = pd.concat(
        [X_train, X_friday_train],
        ignore_index=True
    )

    y_train_all = pd.concat(
        [y_train, y_friday_train],
        ignore_index=True
    )

    print("\nCombined training shape:", X_train_all.shape)
    print("\nCombined training class distribution:")
    print(y_train_all.value_counts())

    # 5. Train the new Random Forest model
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    print("\nTraining the new model...")
    model.fit(X_train_all, y_train_all)

    print("Model training completed!")

    # 6. Evaluate on the held-out Tuesday + Wednesday test data
    evaluate_model(
        model,
        X_test,
        y_test,
        "Tuesday + Wednesday holdout"
    )

    # 7. Evaluate on Friday data that was not used for training
    evaluate_model(
        model,
        X_friday_test,
        y_friday_test,
        "Friday holdout"
    )

    # 8. Save the experiment model without overwriting the original
    MODEL_DIR.mkdir(exist_ok=True)

    model_path = MODEL_DIR / "random_forest_friday_experiment.joblib"
    joblib.dump(model, model_path)

    print(f"\nExperiment model saved to: {model_path}")
