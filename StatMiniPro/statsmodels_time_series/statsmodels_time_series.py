#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.datasets import co2

# Load dataset
co2_data = co2.load_pandas().data
co2_data = co2_data.resample('W').mean().ffill()  # weekly average and forward fill missing values

# Fit ARIMA model (ARIMA(p=1,d=1,q=1))
model = ARIMA(co2_data['co2'], order=(1, 1, 1))
model_fit = model.fit()

# Forecast the next 52 weeks
forecast_steps = 52
forecast = model_fit.forecast(steps=forecast_steps)

# Plot observed and forecast values
plt.figure()
plt.plot(co2_data.index, co2_data['co2'], label='Observed')
forecast_index = pd.date_range(start=co2_data.index[-1] + pd.Timedelta(weeks=1), periods=forecast_steps, freq='W')
plt.plot(forecast_index, forecast, label='Forecast')
plt.title('CO₂ Weekly Observations and Forecast')
plt.xlabel('Date')
plt.ylabel('CO₂ Concentration')
plt.legend()
plt.tight_layout()
plt.savefig('forecast.png')
print('Forecast plot saved as forecast.png.')
