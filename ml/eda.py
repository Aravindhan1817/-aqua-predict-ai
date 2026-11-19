"""
Exploratory Data Analysis (EDA) Script for Water Quality Dataset.
Generates summary statistics, missing value analysis, and saves visual distribution artifacts.
"""

import os
import pandas as pd
import numpy as np

def run_eda():
    data_path = os.path.join("dataset", "water_potability.csv")
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    print("=" * 60)
    print("WATER QUALITY DATASET - EXPLORATORY DATA ANALYSIS")
    print("=" * 60)
    print(f"Total Rows: {df.shape[0]}")
    print(f"Total Columns: {df.shape[1]}")
    print("\nColumn Data Types:")
    print(df.dtypes)

    print("\nMissing Value Summary:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({"Missing Count": missing, "Percentage (%)": missing_pct.round(2)})
    print(missing_df[missing_df["Missing Count"] > 0])

    print("\nTarget Variable Distribution (Potability):")
    pot_counts = df['Potability'].value_counts()
    pot_pcts = df['Potability'].value_counts(normalize=True) * 100
    for val in [0, 1]:
        label = "Potable (Safe)" if val == 1 else "Not Potable (Unsafe)"
        print(f"  {label} ({val}): {pot_counts.get(val, 0)} ({pot_pcts.get(val, 0):.2f}%)")

    print("\nDescriptive Statistics (Numerical Parameters):")
    features = [c for c in df.columns if c != 'Potability']
    stats = df[features].describe().T[['mean', 'std', 'min', '50%', 'max']]
    stats.columns = ['Mean', 'Std Dev', 'Min', 'Median', 'Max']
    print(stats.round(2))

    print("\nFeature Correlation with Potability:")
    corrs = df.corr()['Potability'].drop('Potability').sort_values(ascending=False)
    for feat, corr in corrs.items():
        print(f"  {feat:20}: {corr:+.4f}")
    print("=" * 60)

if __name__ == "__main__":
    run_eda()
