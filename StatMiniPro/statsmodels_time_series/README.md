# Time-Series Forecasting with Statsmodels

This project demonstrates time-series modeling using the `statsmodels` library. It uses the `co2` dataset from the statsmodels package to illustrate forecasting with an AutoRegressive Integrated Moving Average (ARIMA) model. Time-series analysis remains a key area of statistics, and emerging applications involve forecasting economic and environmental trends. The project shows how ARIMA models can capture temporal patterns and generate future forecasts.

## Background
Recent research emphasises that statistical analysis methods need to adapt to the complexity of modern datasets. New approaches such as machine learning and deep learning complement traditional statistical methods【461678192689627†L162-L175】. However, classical time-series models remain valuable, especially when they are integrated with modern tools.

## Dataset
We use the `co2` dataset from statsmodels, which records weekly atmospheric CO₂ concentrations. This dataset is routinely used in climate studies.

## How to Use
Run `python time_series_forecasting.py` to load the data, fit an ARIMA model, and plot the forecast. The script automatically handles missing values by forward-filling.

## Dependencies
See `requirements.txt` for required Python packages.