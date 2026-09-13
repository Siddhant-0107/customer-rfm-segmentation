"""Tests for the RFM pipeline."""

import pandas as pd

from src.cleaning import clean_transactions
from src.rfm import build_rfm
from src.segmentation import add_segments


def sample_transactions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "transaction_id": ["T1", "T2", "T3", "T4"],
            "customer_id": ["C1", "C1", "C2", "C2"],
            "transaction_date": pd.to_datetime(
                ["2025-01-01", "2025-01-10", "2025-01-05", "2025-01-05"]
            ),
            "amount": [100.0, 200.0, 50.0, 75.0],
            "product_category": ["Grocery"] * 4,
            "channel": ["Online"] * 4,
        }
    )


def test_clean_transactions_removes_invalid_rows_and_duplicates() -> None:
    df = sample_transactions()
    invalid = df.iloc[[0]].copy()
    invalid["amount"] = -10
    duplicate = df.iloc[[1]].copy()
    cleaned = clean_transactions(pd.concat([df, invalid, duplicate], ignore_index=True))

    assert cleaned["transaction_id"].is_unique
    assert (cleaned["amount"] > 0).all()
    assert len(cleaned) == 4


def test_frequency_and_monetary_are_calculated_correctly() -> None:
    rfm = build_rfm(sample_transactions(), analysis_date=pd.Timestamp("2025-01-11"))
    c1 = rfm.loc[rfm["customer_id"] == "C1"].iloc[0]
    assert c1["frequency"] == 2
    assert c1["monetary"] == 300.0
    assert c1["recency"] == 1


def test_rfm_scores_are_between_one_and_five() -> None:
    transactions = sample_transactions()
    transactions = pd.concat([transactions] * 5, ignore_index=True)
    transactions["transaction_id"] = [f"T{i}" for i in range(len(transactions))]
    transactions["customer_id"] = ["C1", "C1", "C2", "C2", "C3"] * 4
    # Add enough unique customers for stable quintiles.
    extra = []
    for i in range(3, 8):
        extra.append(
            {
                "transaction_id": f"EX{i}",
                "customer_id": f"C{i}",
                "transaction_date": pd.Timestamp("2025-01-01") + pd.Timedelta(days=i),
                "amount": float(100 * i),
                "product_category": "Grocery",
                "channel": "Online",
            }
        )
    transactions = pd.concat([transactions, pd.DataFrame(extra)], ignore_index=True)

    rfm = build_rfm(transactions, analysis_date=pd.Timestamp("2025-02-01"))
    for column in ["r_score", "f_score", "m_score"]:
        assert rfm[column].between(1, 5).all()


def test_segments_are_business_facing_labels() -> None:
    transactions = sample_transactions()
    transactions = pd.concat([transactions] * 4, ignore_index=True)
    transactions["transaction_id"] = [f"T{i}" for i in range(len(transactions))]
    transactions["customer_id"] = ["C1", "C1", "C2", "C2"] * 4
    for i in range(3, 9):
        transactions = pd.concat(
            [
                transactions,
                pd.DataFrame(
                    [
                        {
                            "transaction_id": f"EX{i}",
                            "customer_id": f"C{i}",
                            "transaction_date": pd.Timestamp("2025-01-01") + pd.Timedelta(days=i),
                            "amount": float(100 * i),
                            "product_category": "Grocery",
                            "channel": "Online",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    rfm = add_segments(build_rfm(transactions, analysis_date=pd.Timestamp("2025-02-01")))
    allowed = {
        "Champions",
        "Loyal Customers",
        "New Customers",
        "At Risk",
        "Lost Customers",
    }
    assert set(rfm["segment"]).issubset(allowed)
