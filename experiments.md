# NetAnomaly â€” Experiment Log

## Experiment 1: Tuesday Baseline

**Training data:** Tuesday brute-force traffic
**Evaluation:** Random stratified train-test split

- Accuracy: 99.99%
- Attack precision: 99.78%
- Attack recall: 99.84%
- Attack F1-score: 99.81%

**Observation:** The model performed very well when training and testing on data from the same dataset.

## Experiment 2: Testing on Wednesday Traffic

**Training data:** Tuesday brute-force traffic
**Evaluation data:** Wednesday DoS traffic

- Accuracy: 66.87%
- Attack recall: 0%

**Observation:** The model failed to detect Wednesday attacks. This showed that performance on one dataset does not guarantee performance on a different dataset.

## Experiment 3: Combined Tuesday and Wednesday Data

**Training data:** Tuesday and Wednesday traffic
**Evaluation:** Random stratified train-test split

- Accuracy: 99.90%
- Attack precision: 99.68%
- Attack recall: 99.85%
- Attack F1-score: 99.77%

**Observation:** The model performed well on a random test split from the combined dataset, but this did not establish its ability to detect unseen traffic.

## Experiment 4: Testing on Friday DDoS Traffic

**Training data:** Tuesday and Wednesday traffic
**Evaluation data:** Friday DDoS traffic

- Accuracy: 52.19%
- Attack precision: 99.79%
- Attack recall: 17.40%
- Attack F1-score: 29.63%

**Confusion matrix:**

| Actual class | Predicted benign | Predicted attack |
|---|---:|---:|
| Benign | 93,204 | 46 |
| Attack | 105,740 | 22,274 |

**Observation:** The model detected 22,274 attacks but missed 105,740. Despite high attack precision, its recall was poor on Friday traffic.

## Main Learning

High accuracy on a random train-test split does not guarantee good performance on new network traffic. Evaluating on different days and attack types is important for understanding generalization.

## Next Experiment

Train a new model using Tuesday and Wednesday data plus a portion of Friday data. Keep the remaining Friday data separate for evaluation to check whether including Friday examples improves DDoS detection.

## Experiment 5: Training with Friday Data

**Training data:** 80% of Friday traffic combined with 80% of Tuesday and Wednesday traffic.

**Evaluation:** Held-out 20% of Friday traffic and held-out 20% of Tuesday and Wednesday traffic.

### Friday holdout results

- Accuracy: 99.95%
- Attack precision: 99.95%
- Attack recall: 99.96%
- Attack F1-score: 99.96%
- Attacks detected: 25,593
- Attacks missed: 10
- Benign false positives: 13

**Observation:** Including Friday traffic in training substantially improved performance on the held-out Friday portion. However, the random split may contain similar traffic patterns in training and testing, so evaluation on a separate capture or day is still needed to assess generalization.

**Saved model:** `models/random_forest_friday_experiment.joblib`

## Experiment 6: Testing on Unseen Thursday Infiltration Traffic

**Training data:** Tuesday, Wednesday, and 80% of Friday traffic
**Evaluation data:** Thursday Infiltration traffic, not used for training

### Results

- Accuracy: 99.86%
- Attack precision: 0.00%
- Attack recall: 0.00%
- Attack F1-score: 0.00%
- Infiltration attacks detected: 0 out of 36
- Infiltration attacks missed: 36
- Benign false positives: 258

**Confusion matrix:**
| Benign | 207,331 | 263 |
| Attack | 36 | 0 |

**Observation:** Despite high overall accuracy, the model failed to detect any of the 36 Infiltration attacks. This indicates poor generalization to this unseen attack type. Because the attack class contains only 36 records, its evaluation metrics are sensitive to individual predictions.

**Next step:** Investigate whether the model assigns low attack probabilities to Infiltration traffic and explore how different decision thresholds affect detection and false alarms. Any threshold selected using Thursday labels must be treated as exploratory, not as an unbiased final evaluation.

**Conclusion:**

Lowering the threshold to 0.10 increased attack recall to 25.00% but generated 3,935 false alarms. At thresholds of 0.30 and 0.50, the model detected none of the 36 Infiltration attacks. These results illustrate the trade-off between attack detection and false alarms. The threshold comparison is exploratory and does not establish a suitable production threshold.

**Limitation:** Thursday's data was used for threshold exploration, so these results are not an independent final evaluation.


## Experiment 7: Exploratory Decision Threshold Comparison

**Evaluation data:** Thursday Infiltration traffic
**Model:** Friday-trained Random Forest

| Metric | Threshold 0.50 | Threshold 0.10 |
|---|---:|---:|
| Attack recall | 0.00% | 5.56% |
| Attack precision | 0.00% | 0.13% |
| Attacks detected | 0 | 2 |
| Attacks missed | 36 | 34 |
| Benign false positives | 263 | 1,490 |
| Accuracy | 99.86% | 99.27% |

**Observation:** Lowering the threshold from 0.50 to 0.10 detected two Infiltration attacks but increased benign false positives from 263 to 1,490. Threshold adjustment alone did not provide satisfactory detection.

**Limitation:** Thursday's labels were used to investigate the threshold. These results are exploratory and should not be presented as unbiased final performance. A threshold should ultimately be selected using separate validation data and then evaluated on untouched test data.

## Experiment 8: Random Forest Feature Importance Analysis

### Objective
Identify the features that contribute most to the trained Random Forest model's predictions and understand which traffic characteristics the model relies on.

### Method
Loaded the trained model from `models/random_forest_friday_experiment.joblib` and extracted its feature importance scores using `feature_importances_`. The features were sorted in descending order, and the top 15 were displayed.

### Results

The five most important features were:

| Feature | Importance Score |
|---|---:|
| Avg Bwd Segment Size | 0.0922 |
| Bwd Packet Length Mean | 0.0727 |
| Bwd Packet Length Max | 0.0617 |
| Bwd Packet Length Std | 0.0544 |
| Packet Length Variance | 0.0529 |

Several of the most important features describe packet lengths and backward traffic characteristics.

### Findings
1. `Avg Bwd Segment Size` had the highest feature importance score of 0.0922.
2. Packet-length-related features accounted for several of the highest importance scores.
3. The model appears to rely substantially on packet-size patterns when making predictions.
4. Feature importance describes the model's overall use of features; it does not establish causation or explain individual missed predictions.

### Conclusion
This experiment identified the features most influential to the trained Random Forest model overall. Since the model failed to detect the 36 Infiltration records in the Thursday dataset at the default threshold of 0.50, further investigation is needed to determine whether differences in traffic patterns contribute to this failure.

### Limitation
Impurity-based feature importance can be biased toward certain types of features and does not measure how well a feature generalizes to unseen attack types. Further validation is required before drawing conclusions about the cause of the Infiltration detection failure.

## Experiment 9: Attack Probability Distribution Analysis

### Objective
Compare the model's predicted attack probabilities for correctly classified benign records, false positives, and missed Infiltration attacks in the unseen Thursday dataset.

### Method
Loaded the trained Random Forest model and evaluated the Thursday Infiltration dataset. Attack probabilities were obtained using `predict_proba()`. Predictions were classified as attacks when the probability was at least 0.50. Probability statistics were then calculated for three groups.

### Results

| Group | Count | Mean probability | Median probability | Minimum | Maximum |
|---|---:|---:|---:|---:|---:|
| Correctly classified benign | 207,331 | 0.0028 | 0.0000 | 0.0000 | 0.4900 |
| False positives | 263 | 0.7257 | 0.7000 | 0.5000 | 1.0000 |
| Missed Infiltration attacks | 36 | 0.0394 | 0.0300 | 0.0000 | 0.3100 |

### Findings
1. Correctly classified benign records generally received very low attack probabilities.
2. The 263 false positives received probabilities of at least 0.50, with a median of 0.70.
3. All 36 Infiltration attacks received probabilities below 0.50 and were classified as benign.
4. The median attack probability for missed Infiltration records was only 0.03.

### Conclusion
The model assigns very low attack probabilities to the unseen Infiltration records, indicating that it fails to recognize them as attacks under the current training and evaluation setup. The results highlight a generalization limitation that requires further investigation.

### Limitation
Probability distributions alone cannot identify the exact cause of the missed detections. The small number of Infiltration records (36) also limits the strength of conclusions about this attack type.

## Experiment 10: Comparing Attack Feature Distributions

### Objective
Compare the `Bwd Packet Length Mean` feature across the attack records in the Tuesday, Wednesday, Friday, and Thursday datasets.

### Method
Loaded the four CIC-IDS2017 parquet datasets and selected records whose labels were not `Benign`. Calculated the count, mean, median, standard deviation, minimum, and maximum for `Bwd Packet Length Mean`.

### Results

| Dataset | Attack type | Count | Mean | Median |
|---|---|---:|---:|---:|
| Tuesday | Brute Force | 9,150 | 33.4555 | 12.5333 |
| Wednesday | DoS | 193,756 | 1,596.6239 | 1,932.5000 |
| Friday | DDoS | 128,014 | 1,481.1444 | 1,934.5000 |
| Thursday | Infiltration | 36 | 7.0394 | 6.0000 |

### Findings
1. The Thursday Infiltration records had a much lower median backward packet length mean than the attack records from the other three datasets.
2. The Tuesday Brute Force dataset had lower values than the Wednesday DoS and Friday DDoS datasets, but its median was still higher than Thursday's.
3. `Bwd Packet Length Mean` is one of the trained model's most important features.
4. The observed distribution difference is consistent with a possible generalization problem, but does not prove the cause of the missed detections.

### Conclusion
The experiment identified a substantial difference in one important feature between the unseen Infiltration records and the attacks represented in the training datasets. Further analysis across multiple features is needed to determine how the attack patterns differ.

### Limitation
Only one feature was examined, and Thursday contains just 36 Infiltration records. These descriptive statistics cannot establish causation or prove that this feature alone explains the model's failure.

## Experiment 11: Comparing Multiple Attack Features

### Objective
Compare the distributions of the five most important Random Forest features across Tuesday Brute Force, Wednesday DoS, Friday DDoS, and Thursday Infiltration attack records.

### Method
Selected attack records from each dataset and calculated the mean and median of the following features: `Avg Bwd Segment Size`, `Bwd Packet Length Mean`, `Bwd Packet Length Max`, `Bwd Packet Length Std`, and `Packet Length Variance`.

### Median Results

| Feature | Tuesday: Brute Force | Wednesday: DoS | Friday: DDoS | Thursday: Infiltration |
|---|---:|---:|---:|---:|
| Avg Bwd Segment Size | 12.5333 | 1932.5000 | 1934.5000 | 6.0000 |
| Bwd Packet Length Mean | 12.5333 | 1932.5000 | 1934.5000 | 6.0000 |
| Bwd Packet Length Max | 34.0000 | 5792.0000 | 5755.0000 | 6.0000 |
| Bwd Packet Length Std | 14.5498 | 2120.7320 | 2189.7730 | 0.0000 |
| Packet Length Variance | 160.7233 | 2627376.0000 | 3625074.0000 | 78793.8906 |

### Findings
1. Thursday Infiltration records had substantially lower medians for several backward packet-length features than Wednesday DoS and Friday DDoS records.
2. The median `Bwd Packet Length Std` was zero for Thursday Infiltration records.
3. `Avg Bwd Segment Size` and `Bwd Packet Length Mean` produced identical statistics, indicating redundant information in these features.
4. The distribution differences are consistent with a possible generalization problem but do not prove the cause of the missed detections.

### Conclusion
The multi-feature comparison identified marked differences between Thursday Infiltration traffic and the attack traffic represented in the other datasets. These differences provide evidence for further investigation into the model's failure to generalize to an unseen attack type.

### Limitations
Thursday contains only 36 Infiltration records. These descriptive statistics do not establish causation, and the five selected features do not represent all information used by the model. Duplicate features also mean that the five-feature comparison does not represent five fully independent signals.

## Experiment 12: Detecting Perfectly Correlated Features

### Objective
Identify pairs of highly related numerical features across the Tuesday, Wednesday, Friday, and Thursday datasets.

### Method
Loaded each dataset, removed the `Label` column, calculated the absolute Pearson correlation matrix, and listed feature pairs with a correlation of exactly 1.0.

### Results

- Tuesday Brute Force: 6 perfectly correlated pairs.
- Wednesday DoS: 6 perfectly correlated pairs.
- Friday DDoS: 8 perfectly correlated pairs.
- Thursday Infiltration: 7 perfectly correlated pairs.

Repeated pairs included:
- `Bwd Packet Length Mean` and `Avg Bwd Segment Size`.
- `Fwd Packet Length Mean` and `Avg Fwd Segment Size`.
- `Total Fwd Packets` and `Subflow Fwd Packets`.
- `Total Backward Packets` and `Subflow Bwd Packets`.
- `Fwd PSH Flags` and `SYN Flag Count`.

### Findings
1. Several feature pairs had perfect positive correlations across multiple datasets.
2. The backward packet-length mean and average backward segment size were perfectly correlated, consistent with their identical summary statistics in earlier experiments.
3. Correlated features can make individual feature-importance scores less straightforward to interpret.

### Conclusion
The experiment identified redundant or perfectly related feature pairs that merit further investigation. Feature removal should be evaluated through controlled model comparisons rather than assumed to improve performance.

### Limitation
Perfect correlation does not always prove that two columns are identical. The experiment also examined each dataset separately and did not establish whether removing these features improves generalization to unseen attack types.

### Experiment 13: Effect of Removing Duplicate Features

**Objective:**
Investigate whether removing duplicate feature columns reduces model complexity without degrading attack detection performance.

**Method:**
- Combined the Tuesday Brute Force, Wednesday DoS, and Friday DDoS datasets.
- Used a stratified 80/20 training-test split.
- Trained a baseline Random Forest using all 77 features.
- Removed 15 duplicate feature columns and trained a second Random Forest using 62 features.
- Evaluated both models on the same test set.

**Results:**

| Metric | All Features | Reduced Features |
|---|---:|---:|
| Number of features | 77 | 62 |
| Accuracy | 99.90% | 99.91% |
| Attack precision | 99.79% | 99.80% |
| Attack recall | 99.84% | 99.87% |
| Attack F1-score | 99.82% | 99.83% |
| False positives | 139 | 132 |
| Missed attacks | 103 | 88 |

**Conclusion:**
Removing 15 duplicate feature columns reduced the feature count by approximately 19.5%. The reduced-feature model achieved slightly better performance on the same test split. This suggests that redundant features may be removed without harming performance in this experiment. Further evaluation on genuinely unseen attack types is required to establish generalization.

**Limitation:**
Both models were evaluated on a random holdout from the combined datasets. These results do not establish reliable detection of previously unseen attack types.

### Experiment 14: Reduced-Feature Model on Unseen Infiltration Data

**Objective:**
Determine whether removing duplicate features improves detection of Infiltration attacks absent from the training datasets.

**Method:**
- Used a stratified sample of 100,000 records from the Tuesday, Wednesday, and Friday datasets.
- Split the sample into 80,000 training records and 20,000 test records.
- Trained two Random Forest models using 20 trees: one with 77 features and one with 62 features.
- Evaluated both models on Thursday's Infiltration dataset, containing 207,594 benign records and 36 attack records.

**Results:**

| Metric | Baseline | Reduced |
|---|---:|---:|
| Features | 77 | 62 |
| Random-test accuracy | 99.82% | 99.84% |
| Random-test attack recall | 99.53% | 99.55% |
| Thursday attack recall | 0% | 0% |
| Thursday attacks missed | 36 | 36 |
| Thursday false positives | 429 | 437 |

**Conclusion:**
Removing duplicate features produced a small improvement on the random test set but did not improve detection of Thursday's Infiltration attacks. Both models missed all 36 attacks. This suggests that redundant features are not the main reason for the observed generalization failure.

**Limitation:**
The Thursday attack class contains only 36 records, so its recall estimate is based on a small number of examples. The sampled training experiment is preliminary and should not be directly compared with full-dataset results.

### Experiment 15: Attack Probability Analysis on Unseen Infiltration Data

**Objective:**
Investigate why the baseline and reduced-feature Random Forest models failed to detect Thursday's Infiltration attacks at the default prediction threshold of 0.5.

**Method:**
- Reused the two models trained on the 100,000-record sample from Tuesday, Wednesday, and Friday.
- Selected the 36 actual Infiltration attack records from Thursday's dataset.
- Examined the predicted attack probabilities for both models.

**Results:**

| Metric | Baseline | Reduced |
|---|---:|---:|
| Mean attack probability | 3.47% | 5.00% |
| Median attack probability | 5% | 5% |
| Maximum attack probability | 10% | 20% |
| Attacks with probability >= 10% | 4 | 9 |
| Attacks with probability >= 25% | 0 | 0 |
| Attacks with probability >= 50% | 0 | 0 |

**Conclusion:**
Both models assigned low attack probabilities to the unseen Infiltration records. The reduced-feature model assigned higher probabilities to some attacks but still failed to classify any of the 36 attacks as malicious at the default threshold. This suggests that removing redundant features alone does not resolve the generalization problem.

**Limitation:**
The analysis uses only 36 Infiltration attacks and a preliminary sample-trained model. Predicted probabilities are model scores, not necessarily calibrated probabilities of malicious activity.

### Experiment 16: Threshold Comparison on Unseen Infiltration Data

**Objective:**
Investigate the trade-off between Infiltration attack detection and false alarms by varying the Random Forest classification threshold.

**Method:**
- Trained a reduced-feature Random Forest on a stratified 100,000-record sample from Tuesday, Wednesday, and Friday.
- Evaluated predicted attack probabilities on Thursday's dataset, containing 36 Infiltration attacks and 207,594 benign records.
- Compared thresholds of 0.10, 0.20, 0.30, and 0.50.

**Results:**

| Threshold | Attacks detected | Attacks missed | False alarms | Attack recall | Attack precision |
|---|---:|---:|---:|---:|---:|
| 0.10 | 9 | 27 | 3,935 | 25.00% | 0.23% |
| 0.20 | 1 | 35 | 1,631 | 2.78% | 0.06% |
| 0.30 | 0 | 36 | 1,051 | 0.00% | 0.00% |
| 0.50 | 0 | 36 | 515 | 0.00% | 0.00% |

**Conclusion:**
Lowering the threshold to 0.10 increased attack recall to 25%, but generated 3,935 false alarms. At thresholds of 0.30 and 0.50,

### Experiment 17: Random Forest vs. Logistic Regression

**Objective:** Compare Random Forest and Logistic Regression on the same sampled dataset and evaluate their performance on Thursday's unseen Infiltration dataset.

**Setup:**
- Training data: Tuesday Brute Force, Wednesday DoS, and Friday DDoS datasets.
- Sample size: 100,000 records.
- Training set: 80,000 records.
- Random test set: 20,000 records.
- Features after duplicate removal: 62.
- Models: Random Forest (20 trees) and Logistic Regression with median imputation and standard scaling.

**Random test results:**

| Metric | Random Forest | Logistic Regression |
|---|---:|---:|
| Accuracy | 99.84% | 96.20% |
| Attack precision | 99.87% | 90.53% |
| Attack recall | 99.55% | 96.37% |
| Attack F1-score | 99.71% | 93.36% |
| False positives | 7 | 558 |
| False negatives | 25 | 201 |

**Thursday Infiltration results:**

- Random Forest: detected 0 of 36 attacks and flagged 437 benign records.
- Logistic Regression: detected 2 of 36 attacks and flagged 7,878 benign records.
- Attack recall: Random Forest 0%; Logistic Regression 5.56%.

**Conclusion:**

Random Forest performed better on the random test set, achieving higher attack precision, recall, and F1-score with fewer false alarms. However, both models performed poorly on Thursday's unseen Infiltration traffic. Logistic Regression detected two attacks but generated many false positives.

The results suggest that performance on familiar attack types does not guarantee generalization to unseen attack types. Thursday's dataset contains only 36 Infiltration attacks, so further validation on additional independently collected attack data is necessary.

**Limitation:** Thursday's data has been used in several exploratory experiments, so it should not be presented as a completely untouched final evaluation set. The random test set also shares attack-day sources with the training data.

**Next step:** Focus on reproducible evaluation and converting NetAnomaly into a usable system, including saved preprocessing and model artifacts, a prediction interface, documentation, and clear limitations.

### Experiment 18: Prediction Pipeline and Friday Sample Evaluation

**Objective:** Validate the saved Random Forest prediction pipeline and evaluate its ability to detect attacks in a sample of Friday DDoS traffic.

**Setup:**
- Model: `models/random_forest.joblib`
- Training data: Tuesday Brute Force and Wednesday DoS datasets.
- Evaluation dataset: Friday DDoS traffic.
- Sample size: 10,000 records, selected with `random_state=42`.

**Results:**

| Metric | Benign | Attack |
|---|---:|---:|
| Precision | 47.06% | 100.00% |
| Recall | 100.00% | 16.76% |
| F1-score | 64.00% | 28.70% |
| Support | 4,253 | 5,747 |

Confusion matrix:

- True negatives: 4,253
- False positives: 0
- False negatives: 4,784
- True positives: 963

Overall accuracy: 52.16%.

**Conclusion:**

The prediction pipeline successfully loaded the saved model and generated predictions for 10,000 network-flow records. However, the model detected only 16.76% of attacks in this Friday sample. It missed 4,784 attacks while producing no false positives.

This result demonstrates poor generalization from Tuesday and Wednesday training traffic to Friday traffic. High precision for attack predictions does not imply that the model detects most attacks.

**Limitation:** This is a diagnostic sample from a dataset already used in earlier experiments, not an independent final evaluation.

**Next step:** Improve the project's usability and documentation while clearly reporting the model's generalization limitations.
 ### Experiment 19: Decision Threshold Analysis

**Objective:** Investigate how the classification threshold affects attack detection on a reproducible sample of 10,000 Friday DDoS traffic records.

**Method:** Loaded the saved Random Forest model, calculated attack probabilities, and evaluated thresholds of 0.10, 0.20, 0.30, 0.40, and 0.50.

**Key findings:**
- At threshold 0.10, the model detected 3,637 of 5,747 attacks, achieving 63.29% recall with 20 false alarms.
- At threshold 0.20, it detected 3,620 attacks, achieving 62.99% recall with only 2 false alarms.
- At threshold 0.50, recall fell to 17.07%, with 4,766 attacks missed.
- Lowering the threshold increased attack detection, but the trade-off varied across thresholds.

**Conclusion:** The default threshold of 0.50 performs poorly for detecting attacks in this Friday sample. Threshold adjustment can improve detection, but the results do not establish an optimal production threshold. A separate validation dataset and an independent test set are needed before choosing a final threshold.

**Limitation:** Friday traffic has been used in earlier experiments, so these results are exploratory rather than an independent final evaluation.

### Experiment 20: Investigating Missed DDoS Attacks

**Objective:** Investigate why the baseline Random Forest model classifies some Friday DDoS attacks as benign.

**Method:** Evaluated a reproducible sample of 10,000 Friday traffic records. Compared attack probabilities and the median values of the eight most important model features for correctly detected and missed attacks.

**Results:**
- Actual attacks: 5,747
- Detected attacks: 963
- Missed attacks: 4,784
- Attack recall at threshold 0.50: 17.07%
- Mean attack probability for missed attacks: 26.38%
- Mean attack probability for detected attacks: 60.39%

**Feature observations:**
- Missed attacks had lower median backward packet length and packet-length variability statistics.
- Median Flow Packets/s was higher for missed attacks (5.374) than detected attacks (0.159).
- These differences suggest that missed and detected attacks have different traffic characteristics.

**Conclusion:** The baseline model struggles to detect many Friday attacks, even though some traffic features differ
The baseline model struggles to detect many Friday attacks, even though some traffic features differ between detected and missed attacks. These feature differences are descriptive observations, not proof of the cause of missed detections.

**Limitation:** This analysis uses a sample from a dataset already examined in earlier experiments. The findings should not be treated as independent validation or evidence of causation.