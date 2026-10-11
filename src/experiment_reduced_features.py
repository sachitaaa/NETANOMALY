
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

FILES = [
    "Bruteforce-Tuesday-no-metadata.parquet",
    "DoS-Wednesday-no-metadata.parquet",
    "DDoS-Friday-no-metadata.parquet",
]

SAMPLE_SIZE = 100_000


if __name__ == "__main__":

    # STEP 1: Load training datasets
    print("Loading training datasets...", flush=True)

    frames = [
        pd.read_parquet(DATA_DIR / filename)
        for filename in FILES
    ]

    df = pd.concat(frames, ignore_index=True)

    X = df.drop(columns=["Label"])
    y = (df["Label"] != "Benign").astype(int)

    # STEP 2: Create a stratified sample
    print("Creating stratified sample...", flush=True)

    X_sample, _, y_sample, _ = train_test_split(
        X,
        y,
        train_size=SAMPLE_SIZE,
        random_state=42,
        stratify=y,
    )

    del df, frames, X, y

    X_train, _, y_train, _ = train_test_split(
        X_sample,
        y_sample,
        test_size=0.20,
        random_state=42,
        stratify=y_sample,
    )

    del X_sample, y_sample

    # STEP 3: Remove duplicate features
    duplicate_columns = X_train.columns[
        X_train.T.duplicated()
    ].tolist()

    X_train_reduced = X_train.drop(
        columns=duplicate_columns
    )

    print("Training records:", len(X_train))
    print("Features before:", X_train.shape[1])
    print("Features after:", X_train_reduced.shape[1])

    # STEP 4: Train the reduced-feature model
    print("\nTraining reduced-feature model...", flush=True)

    model = RandomForestClassifier(
        n_estimators=20,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    y_train = y_train.loc[X_train.index]
    model.fit(X_train_reduced, y_train)

    # STEP 5: Load Thursday's unseen dataset
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

    X_thursday_reduced = X_thursday[
        X_train_reduced.columns
    ]

    # STEP 6: Get attack probabilities once
    print("\nCalculating attack probabilities...", flush=True)

    probabilities = model.predict_proba(
        X_thursday_reduced
    )[:, 1]

    # STEP 7: Compare different thresholds
    print("\n" + "=" * 75)
    print("EXPERIMENT 16: THRESHOLD COMPARISON")
    print("=" * 75)

    thresholds = [0.10, 0.20, 0.30, 0.50]

    for threshold in thresholds:

        predictions = (probabilities >= threshold).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_thursday,
            predictions,
            labels=[0, 1],
        ).ravel()

        recall = tp / (tp + fn) if (tp + fn) else 0
        precision = tp / (tp + fp) if (tp + fp) else 0

        print(f"\nThreshold: {threshold:.2f}")
        print(f"Attacks detected: {tp} / {tp + fn}")
        print(f"Attacks missed: {fn}")
        print(f"False alarms: {fp}")
        print(f"Attack recall: {recall:.2%}")
        print(f"Attack precision: {precision:.2%}")

    print("\nExperiment 16 completed!", flush=True)
