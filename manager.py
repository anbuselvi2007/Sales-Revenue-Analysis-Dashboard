import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Set random seed for reproducibility
np.random.seed(42)

# --- STEP 1: GENERATE HISTORICAL DATASET ---
# Creating 36 months of historical sales data with an upward trend and seasonal peaks
dates = pd.date_range(start="2023-01-01", periods=36, freq="ME")
base_sales = np.linspace(50000, 95000, 36)  # Upward baseline growth
seasonal_effect = 15000 * np.sin(2 * np.pi * dates.month / 12)  # Yearly cyclical peaks
noise = np.random.normal(0, 4000, 36)  # Random real-world noise

historical_sales = base_sales + seasonal_effect + noise

df = pd.DataFrame({"Date": dates, "Sales": historical_sales})
df.set_index("Date", inplace=True)

# --- STEP 2: SPLIT DATA FOR VALIDATION ---
# Split into training (first 30 months) and testing (last 6 months) to evaluate accuracy
train_data = df.iloc[:-6]
test_data = df.iloc[-6:]

# --- STEP 3: TRAIN THE PREDICTIVE MODEL ---
# Fit an ARIMA model (p=1, d=1, q=1 is a standard baseline for trended data)
model = ARIMA(train_data["Sales"], order=(1, 1, 1))
model_fitted = model.fit()

# --- STEP 4: FORECAST FUTURE TRENDS ---
# Forecast the 6-month test period + 6 months into the unknown future (12 months total)
forecast_steps = 12
forecast_results = model_fitted.get_forecast(steps=forecast_steps)

forecast_index = pd.date_range(start=train_data.index[-1] + pd.offsets.MonthEnd(), periods=forecast_steps, freq="ME")
forecast_series = pd.Series(forecast_results.predicted_mean.values, index=forecast_index)

# Get confidence intervals for the predictions (measures uncertainty)
confidence_intervals = forecast_results.conf_int()
confidence_intervals.index = forecast_index

# --- STEP 5: EVALUATE MODEL ACCURACY ---
# Compare the model's predictions against the actual values from our 6-month test split
y_true = test_data["Sales"]
y_pred = forecast_series.loc[test_data.index]

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))

print("=== MODEL ACCURACY METRICS ===")
print(f"Mean Absolute Error (MAE): ${mae:,.2f}")
print(f"Root Mean Squared Error (RMSE): ${rmse:,.2f}")
print("==============================")

# --- STEP 6: VISUALIZE PREDICTIONS ---
plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")

# Plot Historical Training Data
plt.plot(train_data.index, train_data["Sales"], label="Historical Training Data", color="#1f77b4", linewidth=2)

# Plot Actual Test Data (Ground Truth)
plt.plot(test_data.index, test_data["Sales"], label="Actual Sales (Test Set)", color="#2ca02c", marker="o", linewidth=2)

# Plot Forecasted Trend
plt.plot(forecast_series.index, forecast_series.values, label="Model Forecast", color="#d62728", linestyle="--", marker="x", linewidth=2)

# Plot Confidence Intervals (Shaded area representing uncertainty)
plt.fill_between(
    confidence_intervals.index,
    confidence_intervals.iloc[:, 0],
    confidence_intervals.iloc[:, 1],
    color="#d62728",
    alpha=0.15,
    label="95% Confidence Interval"
)

plt.title("Sales & Revenue Predictive Trend Forecast", fontsize=14, fontweight="bold")
plt.xlabel("Timeline", fontsize=12)
plt.ylabel("Sales ($)", fontsize=12)
plt.legend(loc="upper left")
plt.tight_layout()

# Render plot
plt.show()