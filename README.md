# Customer RFM Segmentation & Retention Analysis

A product-analytics portfolio project that turns transaction history into **customer segments, retention priorities, and actionable business recommendations** using Recency, Frequency, and Monetary (RFM) analysis.

## Why this project?

A business should not treat every customer the same way. Some customers are highly engaged and valuable, some are new and need a second-purchase nudge, while others show signs of churn.

This project answers a practical product/business question:

> **Who should the business retain, grow, reactivate, or deprioritize — and why?**

The analysis is deliberately focused on interpretable customer analytics rather than machine learning. RFM provides a simple framework for prioritizing customers from observed purchasing behavior.

## Business Questions

- Who are the highest-value customers?
- Which customers purchase most frequently?
- Which customers have not purchased recently?
- Which segments contribute the most revenue?
- Where is the largest retention/reactivation opportunity?
- What action should the business take for each segment?

## Analytical Workflow

```text
Raw Transactions
       ↓
Data Cleaning & Validation
       ↓
Customer-Level Aggregation
       ↓
Recency / Frequency / Monetary
       ↓
Quintile Scoring (1–5)
       ↓
RFM Score (3–15)
       ↓
Business Segmentation
       ↓
Segment Performance Analysis
       ↓
Retention Recommendations
       ↓
Interactive Streamlit Dashboard
```

## Dataset

The project uses synthetic transaction data so the complete pipeline can be reproduced without exposing real customer information.

`generate_data.py` creates approximately **75,000 transactions across 10,000 customers over 12 months** and intentionally injects a small number of missing, invalid, and duplicate records to demonstrate the cleaning workflow.

For the current generated dataset:

- Raw transactions: **75,020**
- Clean transactions: **74,900**
- Customers retained after cleaning: **9,731**
- Transaction period: **1 Jan 2025 – 31 Dec 2025**
- Customer-level RFM records: **9,731**

### Transaction fields

| Field | Description |
|---|---|
| `transaction_id` | Unique transaction identifier |
| `customer_id` | Customer identifier |
| `transaction_date` | Transaction timestamp/date |
| `amount` | Transaction value |
| `product_category` | Product category |
| `channel` | Purchase channel |

## Data Cleaning

The cleaning pipeline applies explicit, auditable rules:

1. Validate that required columns are present.
2. Parse transaction dates and numeric amounts.
3. Remove rows with missing transaction ID, customer ID, date, or amount.
4. Remove transactions with non-positive amounts.
5. Remove duplicate transaction IDs.
6. Standardize customer and transaction IDs as strings.
7. Sort the cleaned dataset chronologically.

This keeps the analytical dataset consistent before calculating customer metrics.

## RFM Methodology

RFM is calculated at the customer level.

| Metric | Definition | Better direction |
|---|---|---|
| **Recency** | Days since the customer's last purchase | Lower |
| **Frequency** | Number of unique transactions | Higher |
| **Monetary** | Total transaction value | Higher |

The analysis date defaults to **one day after the latest transaction date**. This avoids treating the latest transaction date as having zero elapsed days.

Each RFM metric is converted into a **1–5 quintile score**. Recency is scored in the reverse direction because fewer days since purchase indicates stronger recent engagement.

The final RFM score is:

```text
RFM Score = R Score + F Score + M Score
Range = 3–15
```

Tied values are kept together during percentile-based scoring rather than being arbitrarily split across different score buckets.

## Customer Segments

The project uses five business-facing segments. These are **explicit project rules**, not universal RFM standards.

| Segment | Rule | Business interpretation | Recommended action |
|---|---|---|---|
| **Champions** | R ≥ 4, F ≥ 4, M ≥ 4 | Highly recent, frequent, high-spend customers | Reward loyalty and protect retention |
| **Loyal Customers** | R ≥ 3, F ≥ 3 | Engaged repeat customers | Cross-sell and upsell |
| **New Customers** | R ≥ 3, F ≤ 2 | Recently engaged but with limited purchase history | Drive the second purchase |
| **At Risk** | R ≤ 2, F ≥ 3 | Previously engaged customers showing declining recency | Prioritize personalized win-back |
| **Lost Customers** | R ≤ 2, F ≤ 2 | Low-frequency customers with poor recent engagement | Test low-cost reactivation |

The rules are designed to cover every possible **R/F score combination**, ensuring every customer receives exactly one segment.

## Key Findings

Using the current generated dataset:

| Segment | Customers | Revenue | Avg Recency | Avg Frequency | Avg Spend | Revenue Share |
|---|---:|---:|---:|---:|---:|---:|
| Champions | 2,096 | ₹48.82M | 11.4 days | 15.7 | ₹23,294 | **44.9%** |
| Loyal Customers | 2,572 | ₹29.71M | 28.0 days | 8.2 | ₹11,552 | **27.3%** |
| New Customers | 1,167 | ₹5.02M | 25.9 days | 3.0 | ₹4,306 | **4.6%** |
| At Risk | 1,516 | ₹16.81M | 94.7 days | 7.6 | ₹11,087 | **15.4%** |
| Lost Customers | 2,380 | ₹8.45M | 152.8 days | 2.5 | ₹3,550 | **7.8%** |

### What the numbers suggest

**1. Champions are disproportionately valuable.**  
About **21.5% of customers generate 44.9% of revenue**, making retention of this group a high-value priority.

**2. At Risk customers represent a meaningful reactivation opportunity.**  
The 1,516 At Risk customers account for approximately **₹16.8M in historical revenue**. Their relatively high average frequency and spend suggest that losing these customers could matter more than simply focusing on customer count.

**3. Lost customers should not automatically receive expensive incentives.**  
The Lost segment is large, but its average spend and frequency are substantially lower. A sensible first step is to test low-cost reactivation before committing significant discount budget.

**4. New customers need a second-purchase strategy.**  
The New segment has recent engagement but low frequency, making onboarding, product education, and targeted second-purchase offers logical interventions.

## Product / Business Recommendations

| Segment | Priority | Suggested intervention | Example KPI |
|---|---|---|---|
| Champions | Protect | Loyalty benefits, early access, personalized experiences | Retention rate |
| Loyal Customers | Grow | Cross-sell, bundles, upsell | Revenue/customer |
| New Customers | Convert | Onboarding and second-purchase nudges | Second-purchase rate |
| At Risk | Recover | Personalized win-back journeys | Reactivation rate |
| Lost Customers | Test | Low-cost reactivation experiments | Reactivation ROI |

The next analytical step would be to validate these recommendations through controlled experiments rather than assuming that every intervention will work.

## Dashboard

The Streamlit dashboard provides:

- Customer and revenue KPIs
- At-Risk customer count
- Champions revenue share
- Transaction date, channel, category, and segment filters
- Customer distribution by segment
- Revenue by segment
- Recency, frequency, and monetary distributions
- Segment performance table
- Customer-level explorer
- Segment-specific business recommendations

RFM metrics are recalculated for the selected transaction scope, so filtered views remain internally consistent with the selected population.

## Project Structure

```text
customer-rfm-segmentation/
├── data/
│   └── transactions.csv          # generated locally; ignored by git
├── src/
│   ├── __init__.py
│   ├── cleaning.py               # validation and transaction cleaning
│   ├── rfm.py                    # customer RFM metrics and scoring
│   └── segmentation.py           # business segment assignment
├── tests/
│   ├── __init__.py
│   └── test_rfm.py
├── app.py                        # Streamlit dashboard
├── generate_data.py              # synthetic data generator
├── requirements.txt
├── README.md
├── PRODUCT_ANALYST_INTERVIEW.md
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

Then open the local Streamlit URL shown in the terminal, normally `http://localhost:8501`.

## Testing

The project includes automated tests for the core RFM pipeline. The tests are intentionally focused on analytical correctness rather than UI behavior.

Run:

```powershell
python -m pytest -q
```

## Limitations & Assumptions

- The dataset is synthetic and does not represent a specific real company's customer base.
- RFM scores are relative to the selected customer population; they are not universal customer-quality scores.
- Segment rules are business assumptions and should be validated against business context and historical outcomes.
- Historical revenue is not the same as future customer value.
- RFM alone does not explain *why* a customer churned.
- The analysis does not model margin, acquisition cost, discounts, customer service interactions, or campaign exposure.
- Recommendations should be validated with experiments and downstream KPIs.

## Future Extensions

Reasonable next steps for a production analytics workflow would include:

- Add campaign exposure and response data.
- Track segment movement over time.
- Measure retention and reactivation cohorts.
- Run controlled win-back experiments.
- Incorporate margin or contribution profit into prioritization.

These are deliberately outside the current scope so that the project remains focused on interpretable product analytics.

## Interview Summary

> I built an RFM-based customer segmentation analysis using transactional data. I cleaned and validated the raw transactions, calculated recency, frequency, and monetary value at the customer level, converted those metrics into quintile scores, and mapped customers into five business-facing segments. I then compared segment size, revenue contribution, and purchasing behavior and translated those findings into retention, growth, and reactivation recommendations. Finally, I built an interactive Streamlit dashboard so the analysis could be explored by transaction scope and customer segment.

## Repository

[GitHub repository](https://github.com/Siddhant-0107/customer-rfm-segmentation)
