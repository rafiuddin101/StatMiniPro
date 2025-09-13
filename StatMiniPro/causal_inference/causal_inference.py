#!/usr/bin/env python3
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

# Set random seed
np.random.seed(42)

# Generate synthetic data
n = 1000
# Covariates
X1 = np.random.normal(size=n)
X2 = np.random.normal(size=n)

# Treatment assignment probability depends on covariates
logit_p = 0.5 * X1 - 0.3 * X2
p_treat = 1 / (1 + np.exp(-logit_p))
T = np.random.binomial(1, p_treat)

# Outcome depends on treatment and covariates
Y0 = 2 + 1.5 * X1 + 0.5 * X2 + np.random.normal(scale=1.0, size=n)
Y1 = Y0 + 2.0  # treatment effect = 2.0
Y = np.where(T == 1, Y1, Y0)

# Estimate propensity scores using logistic regression
covariates = np.column_stack((X1, X2))
log_model = LogisticRegression()
log_model.fit(covariates, T)
propensity_scores = log_model.predict_proba(covariates)[:,1]

# Compute ATT using inverse probability weighting
weights = T / propensity_scores
weighted_outcome_treated = weights * Y
# Weighted average for treated group
ATT = weighted_outcome_treated.sum() / weights.sum() - (Y[T==0].mean())

print(f'Estimated ATT (inverse probability weighting): {ATT:.3f}')
