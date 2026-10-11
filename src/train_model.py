import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_dataset(filename):
    """Load one Parquet dataset from the data directory."""
    file_path = DATA_DIR / filename
    return pd.read_parquet(file_path)


def prepare_data(df):
    """Separate input features from the binary target."""
    X = df.drop(columns=["Label"])
    y = (df["Label"] != "Benign").astype(int)

    return X, y


if __name__ == "__main__":
    df_tuesday = load_dataset("Bruteforce-Tuesday-no-metadata.parquet")
    df_wednesday = load_dataset("DoS-Wednesday-no-metadata.parquet")

    df_combined = pd.concat([df_tuesday, df_wednesday], ignore_index=True)

    X, y = prepare_data(df_combined)

    print("Feature shape:", X.shape)
    print("\nBinary target distribution:")
    print(y.value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("\nTraining samples:", len(X_train))
    print("Testing samples:", len(X_test))
    print("\nTraining class distribution:")
    print(y_train.value_counts())
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    print("\nModel training completed!")
    y_pred = model.predict(X_test)

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        y_pred,
        target_names=["Benign", "Attack"],
        digits=4,
        zero_division=0
    ))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    model_dir = Path(__file__).resolve().parent.parent / "models"
    model_dir.mkdir(exist_ok=True)

    model_path = model_dir / "random_forest.joblib"
    joblib.dump(model, model_path)

    print(f"\nModel saved to: {model_path}")



    # Evaluate on unseen Friday DDoS traffic
    print("\nTesting on unseen Friday DDoS data...")

    df_friday = load_dataset("DDoS-Friday-no-metadata.parquet")

    print("\nFriday label distribution:")
    print(df_friday["Label"].value_counts())

    X_friday, y_friday = prepare_data(df_friday)
    y_friday_pred = model.predict(X_friday)



    print("\nFriday Classification Report:")
    print(classification_report(
        y_friday,
        y_friday_pred,
        target_names=["Benign", "Attack"],
        digits=4,
        zero_division=0
    ))

    print("\nFriday Confusion Matrix:")
    print(confusion_matrix(y_friday, y_friday_pred))
