
import joblib
import pandas as pd
from pathlib import Path
from sklearn.metrics import confusion_matrix

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
MODEL_PATH = PROJECT_DIR / "models" / "random_forest.joblib"


def main():
    # Load the saved model.
    model = joblib.load(MODEL_PATH)

    # Load Friday DDoS traffic.
    dataset_path = DATA_DIR / "DDoS-Friday-no-metadata.parquet"
    df = pd.read_parquet(dataset_path)

    # Select the same reproducible sample used earlier.
    sample = df.sample(
        n=min(10000, len(df)),
        random_state=42
    ).copy()

    # Separate input features from actual labels.
    X = sample.drop(columns=["Label"])
    y_actual = (sample["Label"] != "Benign").astype(int)

    # Match the feature columns and order used during training.
    X = X.reindex(columns=model.feature_names_in_)

    # Predict labels and attack probabilities.
    y_pred = model.predict(X)
    attack_column = list(model.classes_).index(1)
    attack_probabilities = model.predict_proba(X)[:, attack_column]

    # Add results to a copy of the sample.
    sample["Actual"] = y_actual.to_numpy()
    sample["Predicted"] = y_pred
    sample["AttackProbability"] = attack_probabilities

    # Identify missed attacks.
    missed_attacks = sample[
        (sample["Actual"] == 1) &
        (sample["Predicted"] == 0)
    ]

    detected_attacks = sample[
        (sample["Actual"] == 1) &
        (sample["Predicted"] == 1)
    ]
    
    # Compare important features of missed and detected attacks.
    attack_mask = sample["Actual"] == 1
    attack_features = X.loc[attack_mask].copy()

    attack_features["Outcome"] = (
        sample.loc[attack_mask, "Predicted"]
        .map({0: "Missed attack", 1: "Detected attack"})
        .to_numpy()
    )

    # Find the eight most important features in the saved model.
    importance = pd.Series(
        model.feature_importances_,
        index=model.feature_names_in_
    ).sort_values(ascending=False)

    top_features = importance.head(8).index

    print("\nTop 8 model features:")
    print(importance.head(8))

    print("\nMedian feature values for missed vs detected attacks:")
    print(
        attack_features.groupby("Outcome")[list(top_features)]
        .median()
        .T
        .to_string()
    )


    print("Records evaluated:", len(sample))
    print("Missed attacks:", len(missed_attacks))
    print("Detected attacks:", len(detected_attacks))

    print("\nMissed-attack probability summary:")
    print(missed_attacks["AttackProbability"].describe())

    print("\nDetected-attack probability summary:")
    print(detected_attacks["AttackProbability"].describe())


if __name__ == "__main__":
    main()
