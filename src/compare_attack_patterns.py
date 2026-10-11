
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

FEATURES = [
    "Avg Bwd Segment Size",
    "Bwd Packet Length Mean",
    "Bwd Packet Length Max",
    "Bwd Packet Length Std",
    "Packet Length Variance",
]

if __name__ == "__main__":
    for name, filename in FILES.items():
        print(f"\n{'=' * 60}")
        print(name)
        print("=" * 60)

        df = pd.read_parquet(DATA_DIR / filename)

        # Keep only attack records
        attacks = df.loc[df["Label"] != "Benign", FEATURES]

        print(f"Attack records: {len(attacks)}")
        print("\nFeature medians:")
        print(attacks.median().round(4))

        print("\nFeature means:")
        print(attacks.mean().round(4))
