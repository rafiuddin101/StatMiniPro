# Bayesian Linear Regression

This project implements a simple Bayesian linear regression model using conjugate priors. We generate synthetic economic data (e.g., GDP growth vs. time) and derive the posterior distribution analytically. Bayesian methods provide a principled approach to incorporate prior knowledge and quantify uncertainty in parameter estimates. Emerging research on macro-economic forecasting uses Bayesian estimation to calibrate complex models such as Dynamic Stochastic General Equilibrium (DSGE) models【581991158043639†L563-L579】.

## Methodology
We assume a normal likelihood with known variance and a normal prior on the regression coefficient. The posterior distribution is then normal with analytically computed mean and variance. We draw samples from the posterior to estimate credible intervals.

## How to Use
Run `python bayesian_regression.py` to simulate data, perform Bayesian inference, and visualize the posterior distribution of the slope parameter.

## Dependencies
See `requirements.txt`.