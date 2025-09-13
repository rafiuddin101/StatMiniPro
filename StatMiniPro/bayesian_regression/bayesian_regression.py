#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

# Generate synthetic data
np.random.seed(42)
n = 100
x = np.linspace(0, 10, n)
true_beta = 3.0
sigma = 1.0
noise = np.random.normal(0, sigma, size=n)
y = true_beta * x + noise

# Prior parameters for beta: Normal(mean=m0, variance=s0^2)
m0 = 0.0
s0_sq = 10.0

# Known variance of noise
sigma_sq = sigma ** 2

# Compute posterior parameters (conjugate normal prior)
# posterior variance = 1 / (1/s0_sq + sum(x^2)/sigma_sq)
posterior_var = 1.0 / (1.0/s0_sq + np.sum(x**2)/sigma_sq)
posterior_mean = posterior_var * (m0/s0_sq + np.sum(x*y)/sigma_sq)

# Draw samples from posterior
num_samples = 1000
posterior_samples = np.random.normal(posterior_mean, np.sqrt(posterior_var), size=num_samples)

# Plot posterior distribution
plt.figure()
plt.hist(posterior_samples, bins=30, density=True)
plt.axvline(true_beta, color='r', linestyle='--', label='True Beta')
plt.axvline(posterior_mean, color='k', linestyle=':', label='Posterior Mean')
plt.title('Posterior Distribution of Beta')
plt.xlabel('Beta')
plt.ylabel('Density')
plt.legend()
plt.tight_layout()
plt.savefig('posterior_beta.png')
print('Posterior plot saved as posterior_beta.png.')

# Print posterior mean and 95% credible interval
lower = np.percentile(posterior_samples, 2.5)
upper = np.percentile(posterior_samples, 97.5)
print(f'Posterior mean: {posterior_mean:.3f}')
print(f'95% credible interval: [{lower:.3f}, {upper:.3f}]')
