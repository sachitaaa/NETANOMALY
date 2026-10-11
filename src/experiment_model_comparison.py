
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

FILES = [
    "Bruteforce-Tuesday-no-metadata.parquet",
    "DoS-Wednesday-no-metadata.parquet",
    "DDoS-Friday-no-metadata.parquet",
]

SAMPLE_SIZE = 100_000


if __name__ == "__main__":

    # STEP 1: Load and sample training data
    print("Loading training datasets...", flush=True)

    frames = [
        pd.read_parquet(DATA_DIR / filename)
        for filename in FILES
    ]

    df = pd.concat(frames, ignore_index=True)

    X = df.drop(columns=["Label"])
    y = (df["Label"] != "Benign").astype(int)

    print("Creating stratified sample...", flush=True)

    X_sample, _, y_sample, _ = train_test_split(
        X,
        y,
        train_size=SAMPLE_SIZE,
        random_state=42,
        stratify=y,
    )

    del df, frames, X, y

    X_train, X_test, y_train, y_test = train_test_split(
        X_sample,
        y_sample,
        test_size=0.20,
        random_state=42,
        stratify=y_sample,
    )

    del X_sample, y_sample

    # Remove duplicate features using training data only
    duplicate_columns = X_train.columns[
        X_train.T.duplicated()
    ].tolist()

    X_train = X_train.drop(columns=duplicate_columns)
    X_test = X_test[X_train.columns]

    print("Training records:", len(X_train))
    print("Features used:", X_train.shape[1])

    # STEP 2: Define two models
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=20,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

        "Logistic Regression": make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(
                class_weight="balanced",
                max_iter=500,
                random_state=42,
            ),
        ),
    }

    # STEP 3: Train and evaluate on random test data
    for name, model in models.items():

        print(f"\nTraining {name}...", flush=True)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        print(f"\n{name} — random test set")
        print(classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["Benign", "Attack"],
            digits=4,
            zero_division=0,
        ))

        print("Confusion matrix:")
        print(confusion_matrix(
            y_test, predictions, labels=[0, 1]
        ))

    # STEP 4: Load Thursday's unseen dataset
    print("\nLoading Thursday Infiltration data...", flush=True)

    thursday_df = pd.read_parquet(
        DATA_DIR / "Infiltration-Thursday-no-metadata.parquet"
    )

    X_thursday = thursday_df.drop(columns=["Label"])
    y_thursday = (
        thursday_df["Label"] != "Benign"
    ).astype(int)

    X_thursday = X_thursday.reindex(
        columns=X_train.columns,
        fill_value=0,
    )

    # STEP 5: Evaluate both models on Thursday
    for name, model in models.items():

        predictions = model.predict(X_thursday)

        print(f"\n{name} — Thursday unseen data")
        print(classification_report(
            y_thursday,
            predictions,
            labels=[0, 1],
            target_names=["Benign", "Attack"],
            digits=4,
            zero_division=0,
        ))

        print("Confusion matrix:")
        print(confusion_matrix(
            y_thursday, predictions, labels=[0, 1]
        ))

    print("\nExperiment 17 completed!", flush=True)
