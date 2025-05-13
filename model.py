import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from joblib import dump
from sklearn.preprocessing import StandardScaler

# Function to apply KMeans clustering to data
def apply_kmeans_clustering(df):
    # Extract features (Amount_INR and standardize it)
    scaler = StandardScaler()
    X = scaler.fit_transform(df[["Amount_INR"]].abs().values)

    # Apply KMeans clustering with 3 clusters
    kmeans = KMeans(n_clusters=3, random_state=42)
    df["Cluster"] = kmeans.fit_predict(X)

    # Calculate cluster centers and sort them
    centers = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_order = centers.argsort(axis=0).ravel()
    
    # Create a mapping from cluster number to label
    cluster_labels = {
        cluster_order[0]: "Low Spend",
        cluster_order[1]: "Medium Spend",
        cluster_order[2]: "High Spend"
    }

    # Assign labels to clusters
    df["Cluster_Label"] = df["Cluster"].map(cluster_labels)
    
    # Save the trained KMeans model and scaler
    dump((kmeans, scaler, cluster_labels), 'kmeans_model.pkl')

    return df

# Visualization for spending by category
def plot_category_spending(df):
    category_spending = df[df['Transaction Type'] == 'debit'].groupby("Category")["Amount_INR"].sum()
    plt.figure(figsize=(10, 6))
    category_spending.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Spending Distribution by Category")
    plt.axis('equal')
    return plt

# Visualization for monthly spending trends
def plot_monthly_spending(df):
    # Convert date to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    
    # Create monthly spending for both credit and debit
    monthly_data = df.pivot_table(
        index=df['Date'].dt.to_period('M'),
        columns='Transaction Type',
        values='Amount_INR',
        aggfunc='sum'
    ).fillna(0)
    
    plt.figure(figsize=(12, 6))
    monthly_data.plot(kind='bar', width=0.8)
    plt.title("Monthly Income vs Expenses")
    plt.xlabel("Month")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=45)
    plt.legend(title="Transaction Type")
    plt.tight_layout()
    return plt

# Visualization for spending clusters
def plot_spending_clusters(df):
    plt.figure(figsize=(10, 6))
    cluster_counts = df["Cluster_Label"].value_counts()
    sns.barplot(x=cluster_counts.index, y=cluster_counts.values, palette="coolwarm")
    plt.title("Distribution of Spending Clusters")
    plt.xlabel("Spending Cluster")
    plt.ylabel("Number of Transactions")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

# Function to get account-wise summary
def get_account_summary(df):
    return df.groupby(['Account Name', 'Transaction Type'])['Amount_INR'].agg(['sum', 'count']).round(2)
