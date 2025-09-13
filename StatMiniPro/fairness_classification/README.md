# Fairness in Machine Learning Classification

This project illustrates fairness considerations in machine learning using a synthetic binary classification problem. We generate a dataset with a sensitive attribute (e.g., group A vs. group B) and train a logistic regression model using `scikit-learn`. We then evaluate demographic parity, a common statistical non-discrimination criterion that equalizes acceptance rates across groups【438854382003095†L4419-L4450】.

Emerging concerns in statistical and machine learning communities involve fairness and bias mitigation. Researchers propose criteria like demographic parity, separation, and sufficiency to quantify fairness in decision-making systems【438854382003095†L4419-L4463】.

## Methodology
1. Generate synthetic data with features, labels, and a binary sensitive attribute.
2. Train a logistic regression classifier.
3. Calculate acceptance rates for each group.
4. Adjust the decision threshold to achieve demographic parity.

## How to Use
Run `python fairness_classification.py` to train the model, compute fairness metrics, and adjust the threshold.

## Dependencies
See `requirements.txt`.