
import joblib
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_DIR / "models" / "random_forest.joblib"

model = joblib.load(MODEL_PATH)

print("Model type:", type(model).__name__)
print("Number of expected features:", model.n_features_in_)

if hasattr(model, "feature_names_in_"):
    features = list(model.feature_names_in_)

    print("\nFirst 10 expected features:")
    for feature in features[:10]:
        print("-", feature)

    print("\nLast 5 expected features:")
    for feature in features[-5:]:
        print("-", feature)
else:
    print("\nFeature names were not saved with this model.")
    print("We will need to recover the feature schema from the training data.")
