
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Business KPI Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Business KPI Dashboard")
st.markdown(
    "### Customer Churn, Retention, Revenue Risk and Customer Segments"
)

# ==========================================
# LOAD DATASET
# ==========================================

@st.cache_data
def load_data():

    file_path = "customer_churn_sample.csv"

    data = pd.read_csv(
        file_path,
        sep=None,
        engine="python",
        header=None,
        encoding="utf-8-sig"
    )

    expected_columns = [
        "CustomerID",
        "Gender",
        "Age",
        "TenureMonths",
        "SubscriptionType",
        "MonthlyCharges",
        "TotalCharges",
        "ContractType",
        "SupportTickets",
        "PaymentMethod",
        "Churn"
    ]

    first_value = str(data.iloc[0, 0]).strip().upper()

    if first_value.startswith("CUST-"):
        data.columns = expected_columns
    else:
        data.columns = [
            str(x).strip().replace('"', "").replace("'", "")
            for x in data.iloc[0]
        ]

        data = data.iloc[1:].reset_index(drop=True)

    data.columns = data.columns.str.strip()

    # Rename dataset columns
    data = data.rename(columns={
        "TenureMonths": "Tenure",
        "ContractType": "Contract",
        "SubscriptionType": "Plan",
        "SupportTickets": "SupportCalls"
    })

    # Convert numerical columns
    numeric_columns = [
        "Age",
        "Tenure",
        "MonthlyCharges",
        "TotalCharges",
        "SupportCalls"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Clean text values
    for column in data.select_dtypes(include="object").columns:
        data[column] = data[column].str.strip()

    return data


try:
    df = load_data()

except Exception as error:
    st.error(f"Dataset loading error: {error}")
    st.stop()


# ==========================================
# CHECK DATASET
# ==========================================

required_columns = [
    "CustomerID",
    "Tenure",
    "Plan",
    "MonthlyCharges",
    "Contract",
    "PaymentMethod",
    "Churn"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.title("🔍 Dashboard Filters")

filtered_df = df.copy()

contracts = sorted(
    df["Contract"].dropna().unique().tolist()
)

selected_contracts = st.sidebar.multiselect(
    "Select Contract",
    contracts,
    default=contracts
)

filtered_df = filtered_df[
    filtered_df["Contract"].isin(selected_contracts)
]

payments = sorted(
    df["PaymentMethod"].dropna().unique().tolist()
)

selected_payments = st.sidebar.multiselect(
    "Select Payment Method",
    payments,
    default=payments
)

filtered_df = filtered_df[
    filtered_df["PaymentMethod"].isin(selected_payments)
]

if df["Tenure"].notna().any():

    min_tenure = int(df["Tenure"].min())
    max_tenure = int(df["Tenure"].max())

    if min_tenure < max_tenure:

        tenure_range = st.sidebar.slider(
            "Select Tenure (Months)",
            min_value=min_tenure,
            max_value=max_tenure,
            value=(min_tenure, max_tenure)
        )

        filtered_df = filtered_df[
            filtered_df["Tenure"].between(
                tenure_range[0],
                tenure_range[1]
            )
        ]

# ==========================================
# KPI CALCULATIONS
# ==========================================

total_customers = len(filtered_df)

churn_mask = (
    filtered_df["Churn"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["yes", "true", "1"])
)

churned_customers = int(churn_mask.sum())

retained_customers = (
    total_customers - churned_customers
)

churn_rate = (
    churned_customers / total_customers * 100
    if total_customers > 0 else 0
)

retention_rate = (
    retained_customers / total_customers * 100
    if total_customers > 0 else 0
)

revenue_at_risk = filtered_df.loc[
    churn_mask, "MonthlyCharges"
].sum()

average_tenure = (
    filtered_df["Tenure"].mean()
    if total_customers > 0 else 0
)

# ==========================================
# KPI DISPLAY
# ==========================================

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Customers",
    total_customers
)

col2.metric(
    "Churn Rate",
    f"{churn_rate:.2f}%"
)

col3.metric(
    "Retention Rate",
    f"{retention_rate:.2f}%"
)

col4.metric(
    "Revenue at Risk",
    f"${revenue_at_risk:,.2f}"
)

col5.metric(
    "Average Tenure",
    f"{average_tenure:.1f} Months"
)

st.caption(
    "Revenue at risk represents monthly charges from customers who churned."
)

# ==========================================
# CUSTOMER ANALYSIS
# ==========================================

st.divider()

st.subheader("📊 Customer Analysis")

if total_customers == 0:

    st.warning("No customers found for the selected filters.")

else:

    col1, col2 = st.columns(2)

    # Churn distribution
    with col1:

        churn_data = (
            filtered_df["Churn"]
            .value_counts()
            .reset_index()
        )

        churn_data.columns = [
            "Churn Status",
            "Customers"
        ]

        fig1 = px.pie(
            churn_data,
            names="Churn Status",
            values="Customers",
            title="Customer Churn Distribution",
            hole=0.4
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    # Contract analysis
    with col2:

        contract_data = (
            filtered_df.groupby(
                ["Contract", "Churn"]
            )
            .size()
            .reset_index(name="Customers")
        )

        fig2 = px.bar(
            contract_data,
            x="Contract",
            y="Customers",
            color="Churn",
            barmode="group",
            title="Churn by Contract Type"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    col3, col4 = st.columns(2)

    # Payment method analysis
    with col3:

        payment_data = (
            filtered_df.groupby(
                ["PaymentMethod", "Churn"]
            )
            .size()
            .reset_index(name="Customers")
        )

        fig3 = px.bar(
            payment_data,
            x="PaymentMethod",
            y="Customers",
            color="Churn",
            barmode="group",
            title="Churn by Payment Method"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    # Tenure analysis
    with col4:

        fig4 = px.histogram(
            filtered_df,
            x="Tenure",
            color="Churn",
            title="Customer Tenure Analysis",
            barmode="overlay"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

# ==========================================
# CUSTOMER SEGMENTS
# ==========================================

st.divider()

st.subheader("👥 Customer Segments")

if total_customers > 0:

    col1, col2 = st.columns(2)

    # Subscription plan
    with col1:

        plan_data = (
            filtered_df.groupby("Plan")
            .size()
            .reset_index(name="Customers")
        )

        fig5 = px.bar(
            plan_data,
            x="Plan",
            y="Customers",
            text="Customers",
            title="Customers by Subscription Plan"
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )

    # Gender distribution
    with col2:

        if "Gender" in filtered_df.columns:

            gender_data = (
                filtered_df.groupby("Gender")
                .size()
                .reset_index(name="Customers")
            )

            fig6 = px.pie(
                gender_data,
                names="Gender",
                values="Customers",
                title="Customer Gender Distribution"
            )

            st.plotly_chart(
                fig6,
                use_container_width=True
            )

# ==========================================
# CUSTOMER DATA TABLE
# ==========================================

st.divider()

st.subheader("📋 Customer Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# DOWNLOAD DATA
# ==========================================

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Customer Data",
    data=csv_data,
    file_name="customer_churn_analysis.csv",
    mime="text/csv"
)

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.success(
    "Business KPI Dashboard Generated Successfully!"
)

st.caption(
    "Business KPI Dashboard | Customer Churn Analysis Project"
)
