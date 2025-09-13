#!/usr/bin/env python3
import numpy as np
from sklearn.linear_model import LogisticRegression

# Generate large synthetic data
np.random.seed(42)
n_samples = 100000
X = np.random.normal(size=(n_samples, 3))
# True coefficients
beta_true = np.array([0.5, -0.8, 0.3])
linear = X.dot(beta_true)
prob = 1 / (1 + np.exp(-linear))
y = np.random.binomial(1, prob)

# Number of chunks
n_chunks = 10
chunk_size = n_samples // n_chunks

# Fit model on full data for comparison
full_model = LogisticRegression(max_iter=200)
full_model.fit(X, y)
full_coef = full_model.coef_[0]

# Fit models on chunks and collect coefficients
chunk_coefs = []
for i in range(n_chunks):
    start = i * chunk_size
    end = (i+1) * chunk_size if i < n_chunks - 1 else n_samples
    X_chunk = X[start:end]
    y_chunk = y[start:end]
    model = LogisticRegression(max_iter=200)
    model.fit(X_chunk, y_chunk)
    chunk_coefs.append(model.coef_[0])

# Average coefficients across chunks
avg_coefs = np.mean(chunk_coefs, axis=0)

print('True coefficients:', beta_true)
print('Full-data model coefficients:', full_coef)
print('Average of chunk coefficients:', avg_coefs)
