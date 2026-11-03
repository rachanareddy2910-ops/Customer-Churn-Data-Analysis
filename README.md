# Customer Churn Data Quality and Exploratory Analysis

## 1. Project Overview
This project focuses on analyzing customer churn data using Python. It identifies missing values, duplicate records, incorrect data, and outliers. The dataset is cleaned and explored to understand customer behavior and churn patterns.

## 2. Objectives
- Identify missing values and duplicate records.
- Check data types and incorrect values.
- Detect outliers in numerical columns.
- Clean and prepare the dataset.
- Perform Exploratory Data Analysis (EDA).
- Understand customer churn patterns using charts.

## 3. Technologies Used
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn

## 4. Dataset Description
The dataset contains customer information such as:
- Customer ID
- Gender
- Age
- Tenure Months
- Subscription Type
- Monthly Charges
- Total Charges
- Contract Type
- Support Tickets
- Payment Method
- Churn Status

## 5. Project Workflow
1. Import the dataset.
2. Inspect the dataset.
3. Identify missing values and duplicates.
4. Detect outliers.
5. Clean the data.
6. Perform exploratory data analysis.
7. Generate charts and a data quality report.

## 6. Project Outputs
- `cleaned_customer_churn.csv` – Cleaned dataset.
- `data_quality_report.txt` – Data quality summary.
- `churn_distribution.png` – Churn distribution chart.
- `tenure_distribution.png` – Customer tenure distribution.
- `monthly_charge_distribution.png` – Monthly charges distribution.
- `churn_by_contract.png` – Churn by contract type.

## 7. How to Run the Project

Install the required libraries:

```bash
pip install -r requirements.txt
```

Run the Python file:

```bash
python customer_churn_analysis.py
```

## 8. Conclusion
This project helps understand customer data quality and customer churn patterns. Data cleaning and exploratory analysis provide useful insights that can support better business decisions.