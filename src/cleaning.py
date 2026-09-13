"""Transaction data cleaning utilities."""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = [
    "transaction_id",
    "customer_id",
    "transaction_date",
    "amount",
    "product_category",
    "channel",
]


def load_transactions(path: str) -> pd.DataFrame:
    """Load a transaction CSV and validate its required columns."""
    df = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transaction records using explicit, auditable rules."""
    cleaned = df.copy()

    cleaned["transaction_date"] = pd.to_datetime(
        cleaned["transaction_date"], errors="coerce"
    )
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")

    cleaned = cleaned.dropna(subset=["transaction_id", "customer_id", "transaction_date", "amount"])
    cleaned = cleaned[cleaned["amount"] > 0]
    cleaned = cleaned.drop_duplicates(subset=["transaction_id"], keep="first")

    cleaned["customer_id"] = cleaned["customer_id"].astype(str)
    cleaned["transaction_id"] = cleaned["transaction_id"].astype(str)

    return cleaned.sort_values("transaction_date").reset_index(drop=True)
