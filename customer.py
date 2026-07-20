import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Set random seed for reproducibility
np.random.seed(42)

# --- step 1: generate synthetic customer dataset ---
# features: Annual Income ($k), Spending Score (1-100), Purchase Frequency (orders/year)
n_customers = 500

data = {
    "CustomerID": range(1001, 1001 + n_customers),
    "Age": np.random.randint(18, 70, size=n_customers),
    "Annual_Income_k$": np.concatenate(
        [
            np.random.normal(30, 8, 150),
            np.random.normal(60, 10, 200),
            np.random.normal(90, 12, 150),
        ]
    ),
    "Spending_Score": np.concatenate(
        [
            np.random.normal(20, 10, 150),
            np.random.normal(50, 12, 200),
            np.random.normal(80, 10, 150),
        ]
    ),
    "Purchase_Frequency": np.concatenate(
        [
            np.random.normal(4, 2, 150),
            np.random.normal(12, 3, 200),
            np.random.normal(25, 5, 150),
        ]
    ),
}

df = pd.DataFrame(data)
# Clip metrics to keep them in realistic bounds
df["Spending_Score"] = df["Spending_Score"].clip(1, 100).astype(int)
df["Annual_Income_k$"] = df["Annual_Income_k$"].clip(15, 150).astype(int)
df["Purchase_Frequency"] = df["Purchase_Frequency"].clip(1, 50).astype(int)


# --- step 2: preprocess the data ---
# Select features relevant to behavior and financial demographics
features = ["Annual_Income_k$", "Spending_Score", "Purchase_Frequency"]
X = df[features]

# Distance-based algorithms like K-Means require feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# --- step 3: execute k-means clustering ---
# We will use 4 clusters to segment the customer base
optimal_clusters = 4
kmeans = KMeans(n_clusters=optimal_clusters, init="k-means++", random_state=42)
df["Segment"] = kmeans.fit_predict(X_scaled)

# Map numeric clusters to meaningful, descriptive business names
segment_labels = {
    0: "Low Spend / Low Frequency",
    1: "High Income / High Spend (VIP)",
    2: "Mid-Tier Mainstream",
    3: "Frugal / High Earners",
}
df["Segment_Name"] = df["Segment"].map(segment_labels)


# --- step 4: generate targeted business insights ---
print("=== CUSTOMER SEGMENT PROFILE SUMMARY ===")
summary = (
    df.groupby("Segment_Name")[features + ["Age"]]
    .mean()
    .sort_values(by="Spending_Score", ascending=False)
)
print(summary.round(1))


# --- step 5: visualize the customer segments ---
plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")

# Plot Income vs Spending Score colored by segment
sns.scatterplot(
    data=df,
    x="Annual_Income_k$",
    y="Spending_Score",
    hue="Segment_Name",
    palette="deep",
    s=70,
    alpha=0.8,
)

plt.title("Customer Segmentation Matrix (Income vs. Spending Score)", fontsize=14)
plt.xlabel("Annual Income (k$)", fontsize=12)
plt.ylabel("Spending Score (1-100)", fontsize=12)
plt.legend(title="Customer Segments", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()

# Display the plot
plt.show()