# Product Analyst Interview Guide

## 1. Give me a 60-second overview of the project.

> I built a customer RFM segmentation and retention analysis using transactional data. I first cleaned and validated the transaction records, then aggregated them to the customer level and calculated Recency, Frequency, and Monetary value. I converted those metrics into 1–5 quintile scores and used explicit business rules to create five segments: Champions, Loyal Customers, New Customers, At Risk, and Lost Customers. I compared customer counts, revenue contribution, and purchasing behavior across the segments, translated the findings into retention and reactivation recommendations, and built a Streamlit dashboard for interactive exploration.

---

## 2. Why did you choose RFM?

RFM is useful because it is:

- Simple to explain to business stakeholders.
- Based on observed customer behavior.
- Useful for prioritizing customers without requiring a predictive model.
- Naturally connected to retention, growth, and reactivation decisions.

The goal of this project was interpretable product analytics, so a transparent framework was more appropriate than adding machine learning simply for complexity.

---

## 3. What do Recency, Frequency, and Monetary mean?

| Metric | Meaning | Better direction |
|---|---|---|
| Recency | Days since the customer's last purchase | Lower |
| Frequency | Number of unique transactions | Higher |
| Monetary | Total amount spent | Higher |

A customer who purchased recently, purchases repeatedly, and spends more will generally receive stronger RFM scores.

---

## 4. Why use quintiles?

The transaction data has customers with very different levels of activity and spending. Quintile scoring converts the raw metrics into a common 1–5 scale, making the three dimensions easier to combine.

It also makes the methodology easy to communicate:

- 1 = relatively weaker performance
- 5 = relatively stronger performance

For Recency, the direction is reversed because fewer days since purchase is better.

The implementation uses percentile ranking with ties preserved rather than arbitrarily splitting equal metric values between score buckets.

---

## 5. Why aren't the segment rules universal?

RFM segmentation does not have one universally correct set of business rules. The thresholds depend on the company's customer behavior, economics, and business objective.

For this project, the rules are explicit assumptions designed to create five interpretable groups and cover every R/F score combination.

The five rules are:

- **Champions:** R ≥ 4, F ≥ 4, M ≥ 4
- **Loyal Customers:** R ≥ 3, F ≥ 3
- **New Customers:** R ≥ 3, F ≤ 2
- **At Risk:** R ≤ 2, F ≥ 3
- **Lost Customers:** R ≤ 2, F ≤ 2

If this were a real product, I would validate the rules against historical retention, conversion, and revenue outcomes before using them operationally.

---

## 6. What was the most important finding?

The strongest finding is revenue concentration.

About **21.5% of customers are Champions, but they generate 44.9% of revenue**. That means retention of high-value customers is potentially more important than optimizing only for the largest customer segment.

A second important finding is the At Risk group: **1,516 customers account for approximately ₹16.8M in historical revenue**. That makes this segment a meaningful retention/reactivation priority.

---

## 7. What would you do with At Risk customers?

I would not immediately send the same discount to everyone.

I would first prioritize the group based on historical value and engagement, then test different interventions such as:

1. Personalized reminders.
2. Relevant product recommendations.
3. Limited-time offers.
4. Loyalty or service-based incentives.

I would measure **reactivation rate, incremental revenue, and campaign ROI**.

The key is to measure incremental impact rather than assuming that a customer who returns after a campaign returned because of the campaign.

---

## 8. What would you do with Champions?

The objective is primarily retention rather than aggressive discounting.

Potential actions:

- Loyalty benefits.
- Early access to new products.
- Personalized recommendations.
- Premium service experiences.
- Cross-sell opportunities where relevant.

The KPI should focus on retention and customer value rather than simply increasing discount-driven transactions.

---

## 9. Why not give large discounts to Lost Customers?

The Lost segment is large, but its average frequency and spend are much lower than Champions and Loyal Customers.

That means a broad, expensive incentive could have poor economics.

I would start with low-cost reactivation experiments and compare the incremental return against the cost of the incentive.

---

## 10. What should happen to New Customers?

The main objective is to increase the probability of a second purchase.

Possible interventions:

- Better onboarding.
- Product education.
- Personalized recommendations.
- Reminder journeys.
- Carefully targeted second-purchase offers.

A useful KPI is **second-purchase rate** within a defined time window.

---

## 11. What are the limitations of this analysis?

The most important limitations are:

- The dataset is synthetic.
- RFM scores are relative to the selected customer population.
- The segment thresholds are assumptions, not validated production thresholds.
- Historical spend is not the same as future customer value.
- RFM does not explain why a customer churned.
- The analysis does not include margin, acquisition cost, discount cost, customer service interactions, or campaign exposure.
- Correlation between segment membership and revenue does not prove that a particular intervention will improve retention.

These limitations are why the recommendations should be validated with experiments and additional behavioral data.

---

## 12. What would you do next if this were a real product?

I would prioritize the following:

### A. Track segment movement over time

Instead of looking at one static snapshot, measure how customers move between New, Loyal, Champions, At Risk, and Lost states.

### B. Add intervention data

Capture campaign exposure, offer type, message, send date, and response.

### C. Run controlled experiments

For example, split an At Risk population into treatment and control groups and measure incremental reactivation.

### D. Add profitability

Revenue alone can be misleading if different customers have very different margins or discount costs.

### E. Build cohort retention views

Measure retention by acquisition month or first-purchase cohort to understand whether customer quality changes over time.

---

## 13. Why did you build a dashboard?

The dashboard turns a static analysis into a tool that a stakeholder can explore.

It allows users to:

- Filter the transaction scope by date.
- Filter by channel and product category.
- Explore customer segments.
- Compare customer count and revenue.
- Inspect RFM distributions.
- Explore individual customer records.
- Connect each segment to a recommended business action.

The goal is not visualization for its own sake. The dashboard is intended to support a business decision about **where to focus retention and growth effort**.

---

## 14. Why does the dashboard recalculate RFM when filters change?

RFM scores are relative to the customer population being analyzed.

If the user changes the date, channel, or product category filters, the relevant transaction population changes. Recalculating RFM keeps the metrics and scores internally consistent with that selected scope.

This behavior is explicitly communicated in the dashboard so users understand that filtered RFM scores are not necessarily the same as the full-population scores.

---

## 15. What SQL questions could you answer from this dataset?

Examples include:

### Revenue by customer

```sql
SELECT
    customer_id,
    SUM(amount) AS total_spend
FROM transactions
GROUP BY customer_id;
```

### Most frequent customers

```sql
SELECT
    customer_id,
    COUNT(DISTINCT transaction_id) AS transaction_count
FROM transactions
GROUP BY customer_id
ORDER BY transaction_count DESC;
```

### Revenue by channel

```sql
SELECT
    channel,
    SUM(amount) AS revenue
FROM transactions
GROUP BY channel
ORDER BY revenue DESC;
```

The Python pipeline was used here because it made the end-to-end RFM workflow and interactive dashboard convenient, but the underlying business questions are equally expressible in SQL.

---

## 16. What makes this a product analytics project rather than just a data science project?

The important part is the decision layer.

The project does not stop at calculating customer scores. It asks:

1. Which customers matter?
2. Why do they matter?
3. Where is the business opportunity?
4. What intervention should be considered?
5. How would we measure whether the intervention worked?

For example, identifying ₹16.8M of historical revenue in the At Risk segment is only useful if it leads to a retention hypothesis and a measurable experiment.

---

## 17. A strong closing statement

> The main lesson from the project is that customer count alone can hide the real business opportunity. In this dataset, Champions are only about one-fifth of customers but contribute nearly half of revenue, while At Risk customers represent a meaningful pool of previously engaged revenue. That is why I would prioritize retention and reactivation based on both engagement and economic value, then validate the resulting strategies through experiments.

---

## Metrics to Remember

For the current generated dataset:

| Metric | Value |
|---|---:|
| Raw transactions | 75,020 |
| Clean transactions | 74,900 |
| Customers | 9,731 |
| Revenue | ₹108.82M |
| Champions | 2,096 customers |
| Champions revenue share | 44.9% |
| At Risk | 1,516 customers |
| At Risk historical revenue | ₹16.81M |
| Lost Customers | 2,380 customers |
| Lost historical revenue | ₹8.45M |

## One-line project pitch

> **An RFM-based customer analytics pipeline that identifies retention and growth opportunities and translates customer behavior into actionable product strategies.**
