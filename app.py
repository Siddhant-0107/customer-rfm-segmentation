"""Streamlit dashboard for Customer RFM Segmentation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from generate_data import main as generate_data
from src.cleaning import clean_transactions, load_transactions
from src.rfm import build_rfm
from src.segmentation import SEGMENT_ACTIONS, add_segments


st.set_page_config(
    page_title="Customer RFM Segmentation",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = Path("data/transactions.csv")
SEGMENT_ORDER = [
    "Champions",
    "Loyal Customers",
    "New Customers",
    "At Risk",
    "Lost Customers",
]


@st.cache_data
def load_transactions_data() -> pd.DataFrame:
    return clean_transactions(load_transactions(str(DATA_PATH)))


st.title("Customer RFM Segmentation")
st.caption(
    "Identify high-value, loyal, new, at-risk, and lost customers from transactional behavior."
)

# The synthetic CSV is intentionally excluded from Git. Generate it automatically
# when the app is deployed so the public dashboard is self-contained.
if not DATA_PATH.exists():
    with st.spinner("Preparing the synthetic transaction dataset..."):
        generate_data()

transactions = load_transactions_data()
min_date = transactions["transaction_date"].min().date()
max_date = transactions["transaction_date"].max().date()

with st.sidebar:
    st.header("Analysis Filters")
    st.caption("RFM metrics recalculate for the selected transaction scope.")

    date_range = st.date_input(
        "Transaction period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
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

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

start_ts = pd.Timestamp(start_date)
end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1)

filtered_transactions = transactions[
    (transactions["transaction_date"] >= start_ts)
    & (transactions["transaction_date"] < end_ts)
    & transactions["channel"].isin(channels)
    & transactions["product_category"].isin(categories)
].copy()

if filtered_transactions.empty:
    st.error("No transactions match the selected filters. Broaden the filters and try again.")
    st.stop()

# The selected period's end is the analysis date so recency is meaningful for the view.
analysis_date = end_ts
rfm = add_segments(build_rfm(filtered_transactions, analysis_date=analysis_date))

with st.sidebar:
    segments = st.multiselect(
        "Customer segment",
        options=SEGMENT_ORDER,
        default=SEGMENT_ORDER,
    )

filtered_rfm = rfm[rfm["segment"].isin(segments)].copy()

if filtered_rfm.empty:
    st.warning("No customers match the selected segment filters.")
    st.stop()

# Customer-level filtering keeps transaction, RFM, and dashboard metrics aligned.
filtered_customer_ids = set(filtered_rfm["customer_id"])
filtered_transactions = filtered_transactions[
    filtered_transactions["customer_id"].isin(filtered_customer_ids)
]

total_customers = filtered_rfm["customer_id"].nunique()
total_revenue = filtered_rfm["monetary"].sum()
avg_customer_value = filtered_rfm["monetary"].mean()
at_risk_customers = (filtered_rfm["segment"] == "At Risk").sum()
champions_revenue = filtered_rfm.loc[
    filtered_rfm["segment"] == "Champions", "monetary"
].sum()
champions_revenue_pct = champions_revenue / total_revenue * 100 if total_revenue else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Customers", f"{total_customers:,}")
c2.metric("Revenue", f"₹{total_revenue:,.0f}")
c3.metric("Avg Customer Value", f"₹{avg_customer_value:,.0f}")
c4.metric("At-Risk Customers", f"{at_risk_customers:,}")
c5.metric("Champions Revenue %", f"{champions_revenue_pct:.1f}%")

st.caption(
    f"Showing {start_date:%d %b %Y} – {end_date:%d %b %Y} | "
    f"{len(filtered_transactions):,} transactions"
)
st.divider()

# Executive insight strip.
segment_revenue = filtered_rfm.groupby("segment")["monetary"].sum()
segment_counts = filtered_rfm["segment"].value_counts()
at_risk_revenue = segment_revenue.get("At Risk", 0)
lost_revenue = segment_revenue.get("Lost Customers", 0)

ins1, ins2, ins3 = st.columns(3)
with ins1:
    st.markdown("**Retention priority**")
    st.write(
        f"{at_risk_customers:,} At-Risk customers represent "
        f"₹{at_risk_revenue:,.0f} in historical revenue."
    )
with ins2:
    st.markdown("**Revenue concentration**")
    st.write(
        f"Champions generate {champions_revenue_pct:.1f}% of revenue, "
        "making retention of this group a high-value priority."
    )
with ins3:
    st.markdown("**Reactivation pool**")
    st.write(
        f"{segment_counts.get('Lost Customers', 0):,} Lost customers account for "
        f"₹{lost_revenue:,.0f}; use low-cost win-back tests before heavy incentives."
    )

left, right = st.columns(2)
with left:
    st.subheader("Customers by Segment")
    counts = (
        filtered_rfm["segment"]
        .value_counts()
        .reindex(SEGMENT_ORDER, fill_value=0)
        .rename_axis("segment")
        .reset_index(name="customers")
    )
    fig = px.pie(
        counts,
        names="segment",
        values="customers",
        hole=0.45,
        category_orders={"segment": SEGMENT_ORDER},
    )
    fig.update_layout(legend_title_text="Segment")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Revenue by Segment")
    revenue = (
        filtered_rfm.groupby("segment", as_index=False)["monetary"]
        .sum()
        .set_index("segment")
        .reindex(SEGMENT_ORDER, fill_value=0)
        .reset_index()
    )
    fig = px.bar(
        revenue,
        x="segment",
        y="monetary",
        text_auto=".2s",
        category_orders={"segment": SEGMENT_ORDER},
    )
    fig.update_layout(yaxis_title="Revenue (₹)", xaxis_title="", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("RFM Distributions")
col1, col2, col3 = st.columns(3)
with col1:
    fig = px.histogram(filtered_rfm, x="recency", nbins=30, title="Recency")
    fig.update_layout(xaxis_title="Days since last purchase", yaxis_title="Customers")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.histogram(filtered_rfm, x="frequency", nbins=30, title="Frequency")
    fig.update_layout(xaxis_title="Number of transactions", yaxis_title="Customers")
    st.plotly_chart(fig, use_container_width=True)
with col3:
    fig = px.histogram(filtered_rfm, x="monetary", nbins=30, title="Monetary")
    fig.update_layout(xaxis_title="Total customer spend (₹)", yaxis_title="Customers")
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
summary["segment"] = pd.Categorical(summary["segment"], categories=SEGMENT_ORDER, ordered=True)
summary = summary.sort_values("segment")

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
explorer_segment = st.selectbox(
    "Explore segment", ["All"] + [s for s in SEGMENT_ORDER if s in filtered_rfm["segment"].unique()]
)
explorer = (
    filtered_rfm
    if explorer_segment == "All"
    else filtered_rfm[filtered_rfm["segment"] == explorer_segment]
)
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
rec_cols = st.columns(len(SEGMENT_ORDER))
for column, segment in zip(rec_cols, SEGMENT_ORDER):
    with column:
        st.markdown(f"**{segment}**")
        st.write(SEGMENT_ACTIONS[segment])

st.caption(
    "RFM is a descriptive segmentation method: scores are relative to the selected customer population "
    "and should be refreshed regularly as customer behavior changes."
)
