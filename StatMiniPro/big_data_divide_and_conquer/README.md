# Big Data Divide-and-Conquer Approach

This project simulates a divide-and-conquer strategy for analyzing large datasets. We generate a large synthetic dataset and partition it into chunks. For each chunk, we fit a logistic regression model to predict a binary outcome. We then average the coefficients across chunks to approximate the full-data model. Such distributed computing approaches are fundamental to big data analytics and are widely studied in the statistical literature【752435895691231†L934-L976】.

## Methodology
1. Generate a large dataset (e.g., 100,000 observations).
2. Split the data into equal-sized chunks.
3. For each chunk, fit a logistic regression using `scikit-learn`.
4. Average the coefficients across chunks.
5. Compare the averaged model coefficients with those from the full dataset.

## How to Use
Run `python divide_and_conquer.py` to perform the simulation and print the results.

## Dependencies
See `requirements.txt`.