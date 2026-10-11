# NetAnomaly — Experiment Log

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
