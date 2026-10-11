# NetAnomaly
### Machine Learning-Based Network Anomaly Detection System

NetAnomaly is an experimental machine learning project that analyzes network-flow data to classify traffic as **Benign** or **Attack** using machine learning.

The project uses the CIC-IDS2017 dataset to investigate network intrusion detection, compare classification models, analyze important features, and evaluate how well models generalize to different attack types.

> **Current status:** Experimental prototype. The models perform well on random test splits but struggle to detect certain attack types in traffic from different days. The project is not production-ready.

## Project Goal

To explore how machine learning can identify potentially malicious network traffic and investigate why models sometimes fail to recognize attacks that differ from their training data.

## Key Features

- Network-flow data analysis using Python and pandas.
- Binary classification: Benign vs. Attack.
- Random Forest model training and evaluation.
- Comparison of Random Forest and Logistic Regression.
- Feature importance and redundant-feature analysis.
- Evaluation using precision, recall, F1-score, and confusion matrices.
- Exploratory testing of classification thresholds.
- A saved-model prediction script.

## Dataset

This project uses the CIC-IDS2017 dataset, with experiments covering:

- **Tuesday:** Brute Force
- **Wednesday:** DoS
- **Thursday:** Infiltration
- **Friday:** DDoS

The original labels are mapped to two classes:

- `0` — Benign
- `1` — Attack

Dataset files are not included in this repository. Place the required Parquet files in the local `data/` directory.

## Models

**Random Forest:** The main model used for training, feature analysis, and prediction experiments.

**Logistic Regression:** A comparison model using median imputation and standard scaling.

## Selected Experimental Findings

- A Random Forest achieved 99.90% accuracy on one random test split using combined Tuesday and Wednesday traffic.
- When evaluated on Friday DDoS traffic without Friday data in training, the model achieved 17.40% attack recall in an earlier full-dataset experiment.
- On a 10,000-record Friday sample, the baseline model achieved 16.76% attack recall and missed 4,784 attacks.
- On Thursday's Infiltration dataset, the baseline model failed to detect all 36 attack records in the evaluated dataset.
- Removing redundant features slightly improved random-test metrics but did not solve the unseen Infiltration detection problem.

These are results from different experiments and evaluation setups; they should not be compared as if they came from one identical test set. Thursday's Infiltration attack class contains only 36 records, which limits the strength of conclusions about that attack type.

See [`experiments.md`](experiments.md) for the detailed experiment log and limitations.

## Project Structure

```text
NetAnomaly/
├── data/                 # Local datasets; not committed
├── models/               # Saved model artifacts; not committed
├── notebooks/            # Exploratory data analysis
├── src/                  # Training, prediction, and experiment scripts
├── experiments.md        # Detailed experiment log
├── README.md
└── .gitignore
```

## Setup

Requirements: Python 3.11 or a compatible version, pip, and the libraries listed below.

Create and activate a virtual environment in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install pandas scikit-learn joblib pyarrow
```

Place the required CIC-IDS2017 Parquet files in `data/`.

## Running the Project

Train the baseline Random Forest model:

```powershell
python src/train_model.py
```

Run the current prediction and diagnostic evaluation script:

```powershell
python src/predict.py
```

The baseline model is saved to `models/random_forest.joblib`.

**Note:** The current `predict.py` script evaluates a sample of Friday traffic. It is a diagnostic script, not yet a general-purpose prediction interface for arbitrary network-flow records.

## Limitations

- Generalization to unseen attack types remains a major challenge.
- Evaluation on different days shows that high random-split accuracy does not guarantee reliable attack detection.
- Some experiments reuse datasets for exploration and threshold analysis; those results are not independent final validation.
- The small number of Thursday Infiltration attacks limits the reliability of attack-specific metrics.
- The system has not been validated for live network deployment.

## Future Work

- Build a reusable prediction interface.
- Save and validate model feature schemas and preprocessing.
- Improve the training, validation, and final testing strategy.
- Evaluate on independently collected traffic and additional attack types.
- Add automated tests and clearer dependency management.
- Build a simple demonstration interface.

## Learning Outcomes

This project explores data preprocessing, classification, feature analysis, model comparison, threshold evaluation, and generalization under changes in network traffic.

**Key lesson:** Strong performance on familiar data does not guarantee reliable detection of previously unseen attacks.
