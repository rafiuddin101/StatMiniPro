#!/usr/bin/env python3
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

# Generate synthetic data
np.random.seed(42)
n = 500
# Features
x1 = np.random.normal(size=n)
x2 = np.random.normal(size=n)
# Sensitive attribute (0 or 1)
sensitive = np.random.binomial(1, 0.5, size=n)
# True coefficients
beta = np.array([1.0, 1.0, 0.5])  # coefficients for x1, x2, sensitive
# Linear combination plus noise
linear = beta[0]*x1 + beta[1]*x2 + beta[2]*sensitive
prob = 1 / (1 + np.exp(-linear))
y = np.random.binomial(1, prob)

# Prepare DataFrame
X = pd.DataFrame({'x1': x1, 'x2': x2, 'sensitive': sensitive})

# Train logistic regression
model = LogisticRegression()
model.fit(X, y)
prob_pred = model.predict_proba(X)[:,1]

# Function to compute acceptance rates by sensitive group given threshold
def acceptance_rate(threshold):
    preds = (prob_pred >= threshold).astype(int)
    rates = {}
    for group in [0,1]:
        mask = (sensitive == group)
        rates[group] = preds[mask].mean()
    return rates

# Default threshold (0.5)
default_rates = acceptance_rate(0.5)
print('Acceptance rates at threshold 0.5:', default_rates)

# Find threshold that equalizes acceptance rates
thresholds = np.linspace(0.1, 0.9, 81)
best_threshold = None
best_diff = 1.0
for t in thresholds:
    rates = acceptance_rate(t)
    diff = abs(rates[0] - rates[1])
    if diff < best_diff:
        best_diff = diff
        best_threshold = t

print(f'Chosen threshold for demographic parity: {best_threshold:.2f}')
print('Acceptance rates at chosen threshold:', acceptance_rate(best_threshold))

# Print confusion matrices for each group at chosen threshold
preds = (prob_pred >= best_threshold).astype(int)
for group in [0,1]:
    mask = (sensitive == group)
    cm = confusion_matrix(y[mask], preds[mask])
    print(f'Confusion matrix for group {group} at threshold {best_threshold:.2f}:
', cm)
