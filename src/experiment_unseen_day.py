
import pandas as pd
import joblib

from pathlib import Path
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


if __name__ == "__main__":

    # 1. Load training datasets
    print("Loading training datasets...")

    df_tuesday = load_dataset(
        "Bruteforce-Tuesday-no-metadata.parquet"
    )
    df_wednesday = load_dataset(
        "DoS-Wednesday-no-metadata.parquet"
    )
    df_friday = load_dataset(
        "DDoS-Friday-no-metadata.parquet"
    )

    df_train = pd.concat(
        [df_tuesday, df_wednesday, df_friday],
        ignore_index=True
    )

    X_train, y_train = prepare_data(df_train)

    print("\nTraining data shape:", X_train.shape)
    print("\nTraining class distribution:")
    print(y_train.value_counts())

    # 2. Load unseen Thursday Infiltration data
    print("\nLoading unseen Thursday Infiltration data...")

    df_thursday = load_dataset(
        "Infiltration-Thursday-no-metadata.parquet"
    )

    X_test, y_test = prepare_data(df_thursday)
    
    # Inspect the 36 actual Thursday infiltration attacks
    thursday_attacks = X_test.loc[y_test == 1]

    inspect_features = [
        "Fwd Packets Length Total",
        "Fwd Act Data Packets",
        "Fwd PSH Flags",
        "SYN Flag Count",
        "Bwd Packet Length Mean",
        "Flow Duration",
    ]

    print("\nThursday infiltration attack feature summary:")
    print(thursday_attacks[inspect_features].describe().T)


    print("\nThursday test shape:", X_test.shape)
    print("\nThursday class distribution:")
    print(y_test.value_counts())
    

    # 3. Check that training and test features match
    if list(X_train.columns) != list(X_test.columns):
        raise ValueError(
            "Training and test features do not match in names or order."
        )

    # 4. Compare median feature values
    # This is exploratory analysis, not proof of causation.
    train_attack_medians = X_train.loc[
        y_train == 1
    ].median(numeric_only=True)

    thursday_attack_medians = X_test.loc[
        y_test == 1
    ].median(numeric_only=True)

    feature_comparison = pd.DataFrame({
        "Training_Attack_Median": train_attack_medians,
        "Thursday_Attack_Median": thursday_attack_medians
    })

    feature_comparison["Absolute_Difference"] = (
        feature_comparison["Training_Attack_Median"]
        - feature_comparison["Thursday_Attack_Median"]
    ).abs()

    print("\nLargest raw median feature differences:")
    print(
        feature_comparison.sort_values(
            "Absolute_Difference",
            ascending=False
        ).head(15)
    )
        # Compare differences relative to training feature variability.
    train_attack_std = X_train.loc[
        y_train == 1
    ].std(numeric_only=True).replace(0, float("nan"))

    feature_comparison["Standardized_Difference"] = (
        feature_comparison["Training_Attack_Median"]
        - feature_comparison["Thursday_Attack_Median"]
    ).abs() / train_attack_std

    print("\nLargest standardized median differences:")
    print(
        feature_comparison.sort_values(
            "Standardized_Difference",
            ascending=False
        )[
            [
                "Training_Attack_Median",
                "Thursday_Attack_Median",
                "Standardized_Difference"
            ]
        ].head(15)
    )

    # 5. Train the Random Forest model
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    print("\nTraining model...")
    model.fit(X_train, y_train)

    # 6. Evaluate on the completely held-out Thursday data
    print("\nEvaluating on unseen Thursday data...")

    y_pred = model.predict(X_test)

    attack_class_index = list(model.classes_).index(1)
    attack_probabilities = model.predict_proba(X_test)[
        :, attack_class_index
    ]

    # Get scores for actual infiltration attacks
    actual_attack_mask = y_test.to_numpy() == 1
    missed_attack_probs = attack_probabilities[
        actual_attack_mask

    ]
    
    # Inspect the 10 infiltration attacks with the highest scores
    attack_rows = X_test.loc[actual_attack_mask].copy()

    attack_rows["Attack_Probability"] = missed_attack_probs

    print("\nTop 10 infiltration attacks by predicted probability:")
    print(
        attack_rows.sort_values(
            "Attack_Probability",
            ascending=False
        )[
            [
                "Attack_Probability",
                "Fwd Packets Length Total",
                "Fwd Act Data Packets",
                "Bwd Packet Length Mean",
                "Flow Duration",
            ]
        ].head(10).to_string(index=False)
    )


    print("\nInfiltration attack probability summary:")
    print(pd.Series(missed_attack_probs).describe())

    # Diagnostic threshold comparison only.
    # Do not select a final threshold using this test set.
    print("\nAttacks detected at different thresholds:")

    for threshold in [0.05, 0.10, 0.20, 0.30, 0.50]:
        detected = missed_attack_probs >= threshold

        print(
            f"Threshold {threshold:.2f}: "
            f"{detected.sum()}/{len(missed_attack_probs)} attacks detected"
        )

    print("\nThursday Classification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=[0, 1],
            target_names=["Benign", "Attack"],
            digits=4,
            zero_division=0
        )
    )

    print("\nThursday Confusion Matrix:")
    print(
        confusion_matrix(
            y_test,
            y_pred,
            labels=[0, 1]
        )
    )

    # 7. Save this experiment model separately
    MODEL_DIR.mkdir(exist_ok=True)

    model_path = MODEL_DIR / "random_forest_unseen_day.joblib"
    joblib.dump(model, model_path)

    print(f"\nExperiment model saved to: {model_path}")
