# Customer RFM Segmentation & Retention Analysis

A placement-focused customer analytics project that uses **Recency, Frequency, and Monetary (RFM)** analysis to segment customers and translate purchasing behavior into retention actions.

## Business Problem

A business cannot treat every customer the same way. This project identifies high-value, loyal, recently acquired, at-risk, and low-engagement customers from transaction history.

## Questions Answered

- Who are the highest-value customers?
- Which customers purchase most frequently?
- Which customers have not purchased recently?
- Which segments generate the most revenue?
- What retention action should be taken for each segment?

## Methodology

1. Generate realistic synthetic transaction data.
2. Clean missing, invalid, and duplicate transaction records.
3. Aggregate transactions to the customer level.
4. Calculate Recency, Frequency, and Monetary value.
5. Convert each metric to a 1-5 quintile score.
6. Combine the scores into an RFM score from 3-15.
7. Map customers into five business-facing segments.
8. Compare customer counts, revenue, recency, frequency, and spend by segment.
9. Explore the results in a Streamlit dashboard.

## RFM Definitions

| Metric | Definition | Better direction |
|---|---|---|
| Recency | Days since the customer's last purchase | Lower |
| Frequency | Number of unique transactions | Higher |
| Monetary | Total transaction value | Higher |

## Customer Segments

| Segment | Rule | Recommended action |
|---|---|---|
| Champions | R >= 4, F >= 4, M >= 4 | Reward loyalty and protect retention |
| Loyal Customers | R >= 3, F >= 4 | Cross-sell and upsell |
| New Customers | R >= 4, F <= 2 | Encourage the second purchase |
| At Risk | R <= 2, F >= 3 | Run targeted win-back campaigns |
| Lost Customers | R <= 2, F <= 2 | Attempt low-cost reactivation |

These rules are explicit project business rules rather than universal RFM standards.

## Project Structure

```text
customer-rfm-segmentation/
├── data/
│   └── transactions.csv          # generated locally; ignored by git
├── src/
│   ├── __init__.py
│   ├── cleaning.py
│   ├── rfm.py
│   └── segmentation.py
├── tests/
│   ├── __init__.py
│   └── test_rfm.py
├── app.py
├── generate_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Run Locally

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Generate the dataset

```powershell
python generate_data.py
```

### 4. Run tests

```powershell
python -m pytest -q
```

### 5. Launch the dashboard

```powershell
python -m streamlit run app.py
```

## Dashboard

The dashboard includes:

- Customer and revenue KPIs
- Customers by segment
- Revenue by segment
- Recency, frequency, and monetary distributions
- Segment performance table
- Segment-based customer explorer
- Business recommendations

## Data

The dataset is intentionally synthetic. `generate_data.py` creates approximately 75,000 transactions across 10,000 customers over 12 months and injects a small number of missing, invalid, and duplicate records so that the cleaning pipeline can be demonstrated.

Generated transaction data is excluded from Git via `.gitignore`.

## Interview Talking Point

> I built an RFM-based customer segmentation analysis using transactional data. I calculated recency, frequency and monetary value at the customer level, converted those metrics into quintile scores, and translated the scores into five business-facing segments. I then compared segment size, revenue contribution and purchasing behavior and turned the findings into retention and reactivation strategies. Finally, I built a Streamlit dashboard for interactive exploration.
