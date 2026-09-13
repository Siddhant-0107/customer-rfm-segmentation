"""RFM metric and quintile scoring utilities."""

from __future__ import annotations

import pandas as pd


def build_rfm(df: pd.DataFrame, analysis_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Aggregate transaction data into one RFM record per customer."""
    if df.empty:
        raise ValueError("Transaction data is empty.")

    analysis_date = analysis_date or (df["transaction_date"].max() + pd.Timedelta(days=1))

    customer_rfm = (
        df.groupby("customer_id")
        .agg(
            last_purchase_date=("transaction_date", "max"),
            frequency=("transaction_id", "nunique"),
            monetary=("amount", "sum"),
        )
        .reset_index()
    )

    customer_rfm["recency"] = (
        analysis_date - customer_rfm["last_purchase_date"]
    ).dt.days
    customer_rfm["rfm_score"] = 0

    # Quintile scoring. Rank first avoids qcut failures caused by tied values.
    customer_rfm["r_score"] = pd.qcut(
        customer_rfm["recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]
    ).astype(int)
    customer_rfm["f_score"] = pd.qcut(
        customer_rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)
    customer_rfm["m_score"] = pd.qcut(
        customer_rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)
    customer_rfm["rfm_score"] = (
        customer_rfm["r_score"]
        + customer_rfm["f_score"]
        + customer_rfm["m_score"]
    )

    return customer_rfm.sort_values("customer_id").reset_index(drop=True)
