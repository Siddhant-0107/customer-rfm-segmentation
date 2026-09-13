"""Business-facing customer segmentation rules."""

from __future__ import annotations

import pandas as pd


def assign_segment(row: pd.Series) -> str:
    """Assign one of five business-facing segments from RFM scores."""
    r, f, m = int(row["r_score"]), int(row["f_score"]), int(row["m_score"])

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 4:
        return "Loyal Customers"
    if r >= 4 and f <= 2:
        return "New Customers"
    if r <= 2 and f >= 3:
        return "At Risk"
    return "Lost Customers"


def add_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    """Return the RFM table with a business segment column."""
    result = rfm.copy()
    result["segment"] = result.apply(assign_segment, axis=1)
    return result


SEGMENT_ACTIONS = {
    "Champions": "Reward loyalty and protect retention.",
    "Loyal Customers": "Increase wallet share through cross-sell and upsell.",
    "New Customers": "Drive the second purchase with onboarding and targeted offers.",
    "At Risk": "Prioritize personalized win-back campaigns.",
    "Lost Customers": "Attempt low-cost reactivation without excessive incentives.",
}
