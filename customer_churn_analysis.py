
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ---------------------------------
# 1. FILE SETTINGS
# ---------------------------------

DATA_FILE = "customer_churn_sample.csv"
OUTPUT_FILE = "cleaned_customer_churn.csv"
REPORT_FILE = "data_quality_report.txt"

# ---------------------------------
# 2. LOAD DATASET
# ---------------------------------

df = pd.read_csv(DATA_FILE, sep="\t")

print("\nCUSTOMER CHURN DATASET")
print("=" * 45)

original_rows = len(df)
original_columns = len(df.columns)

print("Original rows:", original_rows)
print("Original columns:", original_columns)

# Standardize column names
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Remove leading/trailing spaces from text
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()

# ---------------------------------
# 3. DATA PROFILE
# ---------------------------------

print("\nCOLUMN INFORMATION")
print(df.info())

print("\nFIRST FIVE RECORDS")
print(df.head())

print("\nMISSING VALUES")
missing = df.isnull().sum()
print(missing)

print("\nDUPLICATE ROWS")
duplicate_rows = df.duplicated().sum()
print(duplicate_rows)

print("\nDATA TYPES")
print(df.dtypes)

# ---------------------------------
# 4. HANDLE DUPLICATES
# ---------------------------------

df = df.drop_duplicates()

# Customer ID should be unique
if "customer_id" in df.columns:
    duplicate_ids = df["customer_id"].duplicated().sum()
    print("\nDuplicate customer IDs:", duplicate_ids)

    df = df.drop_duplicates(
        subset=["customer_id"],
        keep="first"
    )

# ---------------------------------
# 5. CLEAN DATA TYPES
# ---------------------------------

numeric_columns = [
    "tenure_months",
    "monthly_charge",
    "support_tickets"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

# Standardize churn values
if "churned" in df.columns:
    df["churned"] = (
        df["churned"]
        .astype("string")
        .str.strip()
        .str.lower()
        .replace({
            "yes": "1",
            "no": "0",
            "true": "1",
            "false": "0"
        })
    )

    df["churned"] = pd.to_numeric(
        df["churned"], errors="coerce"
    )

# ---------------------------------
# 6. HANDLE INVALID VALUES
# ---------------------------------

invalid_counts = {}

for col in [
    "tenure_months",
    "monthly_charge",
    "support_tickets"
]:
    if col in df.columns:
        invalid = df[col] < 0
        invalid_counts[col] = int(invalid.sum())

        # Negative values are impossible
        df.loc[invalid, col] = np.nan

# Churn must be either 0 or 1
if "churned" in df.columns:
    invalid_churn = ~df["churned"].isin([0, 1])
    invalid_counts["churned"] = int(invalid_churn.sum())

    df.loc[invalid_churn, "churned"] = np.nan

# ---------------------------------
# 7. HANDLE MISSING VALUES
# ---------------------------------

# ---------------------------------
# 7. HANDLE MISSING VALUES
# ---------------------------------

missing_churn = 0

if "churned" in df.columns:
    missing_churn = int(df["churned"].isna().sum())
    df = df.dropna(subset=["churned"])

for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        if df[col].isnull().any():
            median_value = df[col].median()
            if pd.notna(median_value):
                df[col] = df[col].fillna(median_value)
    else:
        df[col] = df[col].fillna("Unknown")
# ---------------------------------
# 8. OUTLIER DETECTION
# ---------------------------------

outlier_counts = {}

for col in numeric_columns:

    if col in df.columns and df[col].notna().any():

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)

        IQR = Q3 - Q1

        lower_limit = Q1 - 1.5 * IQR
        upper_limit = Q3 + 1.5 * IQR

        outliers = (
            (df[col] < lower_limit) |
            (df[col] > upper_limit)
        )

        outlier_counts[col] = int(outliers.sum())

# Outliers are reported, not automatically deleted.
# This avoids losing potentially valid customers.

# ---------------------------------
# 9. SUMMARY STATISTICS
# ---------------------------------

print("\nSUMMARY STATISTICS")
print(df.describe(include="all"))

# ---------------------------------
# 10. CUSTOMER CHURN ANALYSIS
# ---------------------------------

if "churned" in df.columns:

    total_customers = len(df)

    churned_customers = int(
        (df["churned"] == 1).sum()
    )

    retained_customers = int(
        (df["churned"] == 0).sum()
    )

    churn_rate = (
        churned_customers / total_customers * 100
        if total_customers else 0
    )

    retention_rate = (
        retained_customers / total_customers * 100
        if total_customers else 0
    )

    print("\nCUSTOMER CHURN ANALYSIS")
    print("Total customers:", total_customers)
    print("Churned customers:", churned_customers)
    print("Retained customers:", retained_customers)
    print("Churn rate:", round(churn_rate, 2), "%")
    print("Retention rate:", round(retention_rate, 2), "%")

# ---------------------------------
# 11. GENERATE GRAPHS
# ---------------------------------

sns.set_theme(style="whitegrid")

# Churn distribution
if "churned" in df.columns:
    plt.figure(figsize=(7, 5))

    sns.countplot(
        data=df,
        x="churned"
    )

    plt.title("Customer Churn Distribution")
    plt.xlabel("Churned (0 = No, 1 = Yes)")
    plt.ylabel("Number of Customers")

    plt.tight_layout()
    plt.savefig("churn_distribution.png")
    plt.show()

# Tenure distribution
if "tenure_months" in df.columns:
    plt.figure(figsize=(7, 5))

    sns.histplot(
        data=df,
        x="tenure_months",
        bins=20,
        kde=True
    )

    plt.title("Customer Tenure Distribution")
    plt.xlabel("Tenure in Months")
    plt.ylabel("Number of Customers")

    plt.tight_layout()
    plt.savefig("tenure_distribution.png")
    plt.show()

# Monthly charge distribution
if "monthly_charge" in df.columns:
    plt.figure(figsize=(7, 5))

    sns.histplot(
        data=df,
        x="monthly_charge",
        bins=20,
        kde=True
    )

    plt.title("Monthly Charge Distribution")
    plt.xlabel("Monthly Charge (INR)")
    plt.ylabel("Number of Customers")

    plt.tight_layout()
    plt.savefig("monthly_charge_distribution.png")
    plt.show()

# Churn by contract type
if "contract_type" in df.columns and "churned" in df.columns:
    plt.figure(figsize=(8, 5))

    sns.countplot(
        data=df,
        x="contract_type",
        hue="churned"
    )

    plt.title("Customer Churn by Contract Type")
    plt.xlabel("Contract Type")
    plt.ylabel("Number of Customers")
    plt.xticks(rotation=15)

    plt.tight_layout()
    plt.savefig("churn_by_contract.png")
    plt.show()

# ---------------------------------
# 12. VALIDATION CHECKS
# ---------------------------------

print("\nVALIDATION CHECKS")

print("Remaining missing values:")
print(df.isnull().sum().sum())

print("Remaining duplicate rows:")
print(df.duplicated().sum())

if "customer_id" in df.columns:
    print(
        "Remaining duplicate customer IDs:",
        df["customer_id"].duplicated().sum()
    )

# ---------------------------------
# 13. EXPORT CLEANED DATASET
# ---------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("\nCleaned dataset saved successfully!")

# ---------------------------------
# 14. CREATE DATA QUALITY REPORT
# ---------------------------------

report = []

report.append("CUSTOMER CHURN DATA QUALITY REPORT")
report.append("=" * 45)

report.append(f"Original rows: {original_rows}")
report.append(f"Original columns: {original_columns}")
report.append(f"Final rows: {len(df)}")
report.append(f"Final columns: {len(df.columns)}")

report.append("\nMISSING VALUES BEFORE CLEANING")
report.append(missing.to_string())

report.append("\nDUPLICATE ROWS BEFORE CLEANING")
report.append(str(duplicate_rows))

report.append("\nINVALID VALUES HANDLED")
report.append(str(invalid_counts))

report.append("\nOUTLIERS IDENTIFIED USING IQR")
report.append(str(outlier_counts))

report.append("\nCLEANING DECISIONS")
report.append("1. Removed exact duplicate rows.")
report.append("2. Kept the first record for duplicate customer IDs.")
report.append("3. Converted numeric fields into numeric data types.")
report.append("4. Replaced impossible negative numeric values with missing values.")
report.append("5. Filled missing numeric values with the median.")
report.append("6. Filled missing text values with Unknown.")
report.append("7. Standardized churned values to 0 and 1.")
report.append("8. Detected outliers using the IQR method.")
report.append("9. Outliers were reported but not automatically removed.")

report.append("\nFINAL VALIDATION")
report.append(f"Remaining missing values: {df.isnull().sum().sum()}")
report.append(f"Remaining duplicate rows: {df.duplicated().sum()}")
report.append(
    f"Rows excluded due to missing churn labels: {missing_churn}"
)

report.append("\nSUMMARY STATISTICS")
report.append(df.describe(include="all").to_string())

if "churned" in df.columns:
    report.append("\nCHURN FINDINGS")
    report.append(f"Churn rate: {churn_rate:.2f}%")
    report.append(f"Retention rate: {retention_rate:.2f}%")

with open(REPORT_FILE, "w", encoding="utf-8") as file:
    file.write("\n".join(report))

print("\nData quality report generated successfully!")
print("All analysis completed!")
