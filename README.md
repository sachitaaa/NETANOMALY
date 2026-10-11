# NetAnomaly
### Machine Learning-Based Network Anomaly Detection System

NetAnomaly is an experimental machine learning project that uses network-flow data to classify traffic as **Benign** or **Attack**. It explores network intrusion detection using the CIC-IDS2017 dataset, compares machine learning models, and investigates why models can fail to generalize to traffic from different days and attack types.

> **Project status:** Experimental prototype. The models show strong performance on some random test splits but struggle to detect certain attacks in unseen-day evaluations. This project is not intended for production deployment.

## Project Objectives

- Build a machine learning pipeline for binary network traffic classification.
- Explore network-flow data and identify useful traffic features.
- Compare classification models and evaluation metrics.
- Investigate the difference between random-split performance and unseen-day generalization.
- Understand the limitations of accuracy when attack classes are highly imbalanced.

## Features

- Exploratory data analysis using pandas, NumPy, Matplotlib, and Seaborn.
- Binary classification: Benign (0) and Attack (1).
- Random Forest training and Logistic Regression comparison.
- Feature importance and redundant-feature analysis.
- Evaluation using precision, recall, F1-score, and confusion matrices.
- Experimental classification-threshold analysis.
- Saved-model prediction and diagnostic scripts.
- Unseen-day evaluation using traffic from different days in CIC-IDS2017.

## Dataset

NetAnomaly uses the **CIC-IDS2017** network intrusion detection dataset.

Experiments include traffic from the following days:

- **Tuesday:** Brute Force
- **Wednesday:** Denial of Service (DoS)
- **Thursday:** Infiltration
- **Friday:** Distributed Denial of Service (DDoS)

The original labels are mapped into two classes:

- `0` — Benign
- `1` — Attack

The dataset is not included in this repository. Obtain it from the official [Canadian Institute for Cybersecurity dataset page](https://www.unb.ca/cic/datasets/ids-2017.html), prepare the required Parquet files, and place them in the local `data/` directory.

## Technology Stack

- **Language:** Python
- **Data processing:** pandas, NumPy
- **Machine learning:** scikit-learn
- **Model persistence:** joblib
- **Visualization:** Matplotlib, Seaborn
- **Data format:** Parquet via PyArrow
- **Development:** Jupyter Notebook

## Project Structure

```text
NetAnomaly/
|-- data/                 # Local datasets; excluded from Git
|-- models/               # Saved models; excluded from Git
|-- notebooks/            # Exploratory data analysis
|-- src/                  # Training, prediction, and experiment scripts
|-- experiments.md        # Detailed experiment log
|-- requirements.txt      # Python dependencies
|-- README.md
|-- .gitignore
```

## Setup

Python 3.11 or a compatible version is recommended.

### 1. Clone the repository

```powershell
git clone https://github.com/sachitaaa/NETANOMALY.git
cd NETANOMALY
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Prepare the dataset

Place the required CIC-IDS2017 Parquet files in the local `data/` directory. Dataset files and generated model artifacts are excluded from Git.

## Running the Project

### Train the baseline model

```powershell
python src/train_model.py
```

### Run the prediction and diagnostic script

```powershell
python src/predict.py
```

### Run the unseen-day experiment

```powershell
python src/experiment_unseen_day.py
```

The unseen-day experiment trains on Tuesday, Wednesday, and Friday traffic and evaluates on Thursday Infiltration traffic. This is a held-out-day experiment, although the result is specific to the dataset and attack records used.

**Note:** `predict.py` currently performs diagnostic evaluation on a sample of Friday traffic. It is not yet a general-purpose prediction interface for arbitrary network-flow records.

## Selected Experimental Findings

Experiments conducted during development produced the following results:

- A Random Forest achieved **99.90% accuracy** on one random test split using combined Tuesday and Wednesday traffic.
- In an earlier experiment trained without Friday traffic, the model achieved **17.40% attack recall** when evaluated on Friday DDoS traffic.
- On a 10,000-record Friday sample, the baseline model achieved **16.76% attack recall**, missing 4,784 attack records under that experiment's prediction setup.
- In the Thursday Infiltration evaluation, the model trained on Tuesday, Wednesday, and Friday traffic failed to detect all 36 infiltration attack records at the default 0.50 threshold.
- Feature analysis showed substantial differences between the training attacks and Thursday's infiltration attacks.

These results come from different experiments and evaluation setups; they should not be compared as though they came from a single test set. The Thursday infiltration evaluation contains only 36 attack records, so conclusions about that attack type remain limited.

See [`experiments.md`](experiments.md) for the detailed experiment history and limitations.

## Limitations

- Generalization to traffic from unseen days and attack types remains a major challenge.
- High accuracy on random splits does not guarantee effective attack detection.
- The small number of Thursday Infiltration attack records limits the reliability of attack-specific conclusions.
- Some threshold and feature investigations are exploratory rather than independent final validation.
- The system has not been validated for live network deployment.
- Performance on CIC-IDS2017 does not establish effectiveness on real-world network traffic.

## Future Work

- Establish a reproducible training, validation, and final testing strategy.
- Develop a reusable prediction interface with feature-schema validation.
- Investigate generalization to additional attack types and independent datasets.
- Add automated tests and improve dependency management.
- Build a simple demonstration interface.

## Learning Outcomes

This project explores data preprocessing, classification, model comparison, feature analysis, threshold evaluation, and the challenges of generalization under changing network traffic patterns.

**Key takeaway:** Strong performance on familiar data does not guarantee reliable detection of previously unseen attacks.
