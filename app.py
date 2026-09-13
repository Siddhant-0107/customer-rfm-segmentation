"""Streamlit dashboard for Customer RFM Segmentation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.cleaning import clean_transactions, load_transactions
from src.rfm import build_rfm
from src.segmentation import SEGMENT_ACTIONS, add_segments


st.set_page_config(
    page_title="Customer RFM Segmentation",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = Path("data/transactions.csv")


@st.cache_data

def load_analysis() -> tuple[pd.DataFrame, pd.DataFrame]:
    transactions = clean_transactions(load_transactions(str(DATA_PATH)))
    rfm = add_segments(build_rfm(transactions))
    return transactions, rfm


st.title("Customer RFM Segmentation")
st.caption("Identify high-value, loyal, new, at-risk, and lost customers from transactional behavior.")

if not DATA_PATH.exists():
    st.warning("Data file not found. Run `python generate_data.py` first.")
    st.stop()

transactions, rfm = load_analysis()

with st.sidebar:
    st.header("Filters")
    segments = st.multiselect(
        "Customer segment",
        options=sorted(rfm["segment"].unique()),
        default=sorted(rfm["segment"].unique()),
    )
    channels = st.multiselect(
        "Channel",
        options=sorted(transactions["channel"].unique()),
        default=sorted(transactions["channel"].unique()),
    )
    categories = st.multiselect(
        "Product category",
        options=sorted(transactions["product_category"].unique()),
        default=sorted(transactions["product_category"].unique()),
    )

filtered_transactions = transactions[
    transactions["channel"].isin(channels)
    & transactions["product_category"].isin(categories)
]

# Keep segment filter customer-level so metrics remain internally consistent.
filtered_customer_ids = set(
    rfm.loc[rfm["segment"].isin(segments), "customer_id"]
)
filtered_rfm = rfm[rfm["customer_id"].isin(filtered_customer_ids)].copy()
filtered_transactions = filtered_transactions[
    filtered_transactions["customer_id"].isin(filtered_customer_ids)
]

total_customers = filtered_rfm["customer_id"].nunique()
total_revenue = filtered_rfm["monetary"].sum()
avg_customer_value = filtered_rfm["monetary"].mean() if total_customers else 0
at_risk_customers = (filtered_rfm["segment"] == "At Risk").sum()
champions_revenue = filtered_rfm.loc[
    filtered_rfm["segment"] == "Champions", "monetary"
].sum()
champions_revenue_pct = (champions_revenue / total_revenue * 100) if total_revenue else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Customers", f"{total_customers:,}")
c2.metric("Total Revenue", f"₹{total_revenue:,.0f}")
c3.metric("Avg Customer Value", f"₹{avg_customer_value:,.0f}")
c4.metric("At-Risk Customers", f"{at_risk_customers:,}")
c5.metric("Champions Revenue %", f"{champions_revenue_pct:.1f}%")

st.divider()

left, right = st.columns(2)
with left:
    st.subheader("Customers by Segment")
    counts = filtered_rfm["segment"].value_counts().reset_index()
    counts.columns = ["segment", "customers"]
    fig = px.pie(counts, names="segment", values="customers", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Revenue by Segment")
    revenue = (
        filtered_rfm.groupby("segment", as_index=False)["monetary"].sum()
        .sort_values("monetary", ascending=False)
    )
    fig = px.bar(revenue, x="segment", y="monetary", text_auto=".2s")
    fig.update_layout(yaxis_title="Revenue", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("RFM Distributions")
col1, col2, col3 = st.columns(3)
with col1:
    fig = px.histogram(filtered_rfm, x="recency", nbins=30, title="Recency")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.histogram(filtered_rfm, x="frequency", nbins=30, title="Frequency")
    st.plotly_chart(fig, use_container_width=True)
with col3:
    fig = px.histogram(filtered_rfm, x="monetary", nbins=30, title="Monetary")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Segment Performance")
summary = (
    filtered_rfm.groupby("segment")
    .agg(
        customers=("customer_id", "nunique"),
        revenue=("monetary", "sum"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
    )
    .reset_index()
)
summary["revenue_pct"] = summary["revenue"] / summary["revenue"].sum() * 100
summary = summary.sort_values("revenue", ascending=False)
st.dataframe(
    summary.style.format(
        {
            "revenue": "₹{:,.0f}",
            "revenue_pct": "{:.1f}%",
            "avg_recency": "{:.1f}",
            "avg_frequency": "{:.1f}",
            "avg_monetary": "₹{:,.0f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Customer Explorer")
explorer_segment = st.selectbox("Explore segment", ["All"] + sorted(filtered_rfm["segment"].unique()))
explorer = filtered_rfm if explorer_segment == "All" else filtered_rfm[filtered_rfm["segment"] == explorer_segment]
explorer = explorer.sort_values("monetary", ascending=False)

st.dataframe(
    explorer[
        [
            "customer_id",
            "recency",
            "frequency",
            "monetary",
            "r_score",
            "f_score",
            "m_score",
            "rfm_score",
            "segment",
        ]
    ].head(100),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Business Recommendations")
rec_cols = st.columns(len(SEGMENT_ACTIONS))
for column, segment in zip(rec_cols, SEGMENT_ACTIONS):
    with column:
        st.markdown(f"**{segment}**")
        st.write(SEGMENT_ACTIONS[segment])
