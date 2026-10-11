
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

FILES = {
    "Tuesday - Brute Force": "Bruteforce-Tuesday-no-metadata.parquet",
    "Wednesday - DoS": "DoS-Wednesday-no-metadata.parquet",
    "Friday - DDoS": "DDoS-Friday-no-metadata.parquet",
    "Thursday - Infiltration": "Infiltration-Thursday-no-metadata.parquet",
}

if __name__ == "__main__":
    for name, filename in FILES.items():
        print(f"\n{'=' * 60}")
        print(name)
        print("=" * 60)

        df = pd.read_parquet(DATA_DIR / filename)
        X = df.drop(columns=["Label"])

        # Find pairs of columns with exactly identical values
        correlation = X.corr().abs()
        duplicate_pairs = []

        columns = correlation.columns

        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                if correlation.iloc[i, j] == 1.0:
                    duplicate_pairs.append(
                        (columns[i], columns[j])
                    )

        print(f"Perfectly correlated feature pairs: {len(duplicate_pairs)}")

        for feature_a, feature_b in duplicate_pairs[:20]:
            print(f"{feature_a} <-> {feature_b}")

        if len(duplicate_pairs) > 20:
            print("Showing only the first 20 pairs.")
