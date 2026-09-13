"""Generate a realistic synthetic transaction dataset for the RFM project."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
N_CUSTOMERS = 10_000
N_TRANSACTIONS = 75_000
START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2025-12-31")


PRODUCT_CATEGORIES = [
    "Electronics",
    "Fashion",
    "Home & Kitchen",
    "Beauty",
    "Sports",
    "Grocery",
]
CHANNELS = ["Online", "Store", "Mobile App"]


def generate_transactions() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)

    customer_ids = np.array([f"C{i:05d}" for i in range(1, N_CUSTOMERS + 1)])

    # Customer propensities make the synthetic data less uniform and more useful
    # for segmentation: some customers naturally buy more often and spend more.
    engagement = rng.lognormal(mean=0.0, sigma=0.7, size=N_CUSTOMERS)
    engagement = engagement / engagement.mean()

    selected_customers = rng.choice(
        customer_ids,
        size=N_TRANSACTIONS,
        replace=True,
        p=engagement / engagement.sum(),
    )

    dates = pd.to_datetime(
        rng.integers(
            START_DATE.value // 86_400_000_000_000,
            (END_DATE.value // 86_400_000_000_000) + 1,
            size=N_TRANSACTIONS,
        ),
        unit="D",
    )

    category = rng.choice(
        PRODUCT_CATEGORIES,
        size=N_TRANSACTIONS,
        p=[0.20, 0.18, 0.18, 0.12, 0.14, 0.18],
    )
    channel = rng.choice(CHANNELS, size=N_TRANSACTIONS, p=[0.52, 0.30, 0.18])

    # Log-normal spend creates a realistic long tail of high-value orders.
    amounts = np.round(rng.lognormal(mean=7.0, sigma=0.75, size=N_TRANSACTIONS), 2)
    amounts = np.clip(amounts, 50, 25_000)

    df = pd.DataFrame(
        {
            "transaction_id": [f"T{i:06d}" for i in range(1, N_TRANSACTIONS + 1)],
            "customer_id": selected_customers,
            "transaction_date": dates,
            "amount": amounts,
            "product_category": category,
            "channel": channel,
        }
    )

    # Small, deliberate quality issues let the cleaning pipeline demonstrate
    # validation instead of assuming perfectly clean source data.
    missing_idx = rng.choice(df.index, size=75, replace=False)
    df.loc[missing_idx[:25], "customer_id"] = np.nan
    df.loc[missing_idx[25:50], "amount"] = np.nan
    df.loc[missing_idx[50:], "transaction_date"] = pd.NaT

    negative_idx = rng.choice(df.index.difference(missing_idx), size=25, replace=False)
    df.loc[negative_idx, "amount"] *= -1

    duplicate_rows = df.iloc[rng.choice(df.index, size=20, replace=False)].copy()
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    return df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)


def main() -> None:
    output_path = Path("data/transactions.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_transactions()
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df):,} transaction rows -> {output_path}")


if __name__ == "__main__":
    main()
