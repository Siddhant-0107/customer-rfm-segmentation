"""RFM metric and quintile scoring utilities."""

from __future__ import annotations

import pandas as pd


def _quintile_score(series: pd.Series, ascending: bool = True) -> pd.Series:
    """Assign stable 1-5 percentile scores without splitting tied values.

    ``rank(method="first")`` can give different scores to customers with the
    same metric value. Percentile ranking keeps tied values together, making
    the scoring easier to explain and more consistent for business use.
    """
    percentile = series.rank(method="average", pct=True, ascending=ascending)
    score = pd.cut(
        percentile,
        bins=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[1, 2, 3, 4, 5],
        include_lowest=True,
    )
    return score.astype(int)


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

    # Higher score = better customer value. Recency is reversed because
    # fewer days since purchase indicates stronger recent engagement.
    customer_rfm["r_score"] = _quintile_score(customer_rfm["recency"], ascending=False)
    customer_rfm["f_score"] = _quintile_score(customer_rfm["frequency"], ascending=True)
    customer_rfm["m_score"] = _quintile_score(customer_rfm["monetary"], ascending=True)
    customer_rfm["rfm_score"] = (
        customer_rfm["r_score"]
        + customer_rfm["f_score"]
        + customer_rfm["m_score"]
    )

    return customer_rfm.sort_values("customer_id").reset_index(drop=True)
