# Business Requirements Document

**Project:** Amazon Marketplace Analytics Data Platform
**Document Owner:** Sachintha KahaweWithana, Business Intelligence Specialist
**Version:** 2.0
**Date:** 31 August 2026
**Status:** Draft — supersedes v1.0

---

## 1. Document Purpose

This BRD defines the business problem, scope, stakeholders, and requirements for a simulated Amazon marketplace analytics platform, built to develop and demonstrate end-to-end BI capability: Python extraction, dbt transformation, Kimball/Medallion warehousing on DuckDB, and Power BI reporting. The business scenario (a multi-category Amazon vendor) is fictional; the engineering and analytical practices are treated as production-grade throughout.

---

## 2. Business Context

An enterprise-scale Amazon marketplace vendor generates order, customer, product, marketing, returns, and support-ticket data across disconnected operational systems. Finance, Marketing, CRM, Logistics, and Customer Experience teams each report from their own extracts, producing inconsistent metrics and no shared view of order-to-cash, retention, or channel performance. Return volumes and support-ticket costs are currently invisible to Finance because that data has never been modeled alongside order financials.

## 3. Project Objective

Build a single warehouse — sourced from five raw operational feeds and modeled as a Kimball star schema on a Bronze → Silver → Gold (Medallion) pipeline in DuckDB — that gives Finance, Marketing, Logistics, CRM, CX, and Product/Inventory teams one conformed, auditable version of the truth, surfaced through Power BI.

---

## 4. Scope

### 4.1 In Scope

- Ingestion of five raw source feeds (Section 6) via Python/Pandas
- Bronze/Silver/Gold transformation in dbt Core against DuckDB
- SCD Type 2 history for Customer and Product master data via dbt snapshots
- Seven fact tables and their conformed dimensions across six data marts: Finance, Marketing, Logistics, CRM, CX, and Product/Inventory (Section 7)
- Handling of partial-coverage sources (returns, support tickets) and late-arriving facts
- Power BI semantic model and DAX measures against the Gold layer
- CSF/KPI definitions per business domain, with lead and lagging metric classification

### 4.2 Out of Scope

- Real-time/streaming ingestion (batch only)
- Any connection to live Amazon Seller Central APIs (dataset is a static Kaggle extract)
- Row-level security / multi-tenant access control
- Forecasting or ML-based models (may follow as a separate phase)
- Cloud deployment (platform runs locally against DuckDB)

---

## 5. Stakeholders and Core Business Questions

| Mart | Stakeholder (simulated) | Objective | Core Business Questions |
|---|---|---|---|
| Finance | VP of Finance | Protect margin, track order health and returns cost | What is net revenue after cost price, tax, and refunds? Which payment methods carry the highest failure/pending rate? What is the return rate and refund cost by product category? |
| Marketing | Director of Growth Marketing | Maximize acquisition efficiency | Which channel × device × campaign combinations convert best? Does device type affect basket size? What is cart abandonment by channel? |
| Logistics | Head of Fulfilment | Control shipping cost and delivery performance | Which shipping methods and warehouses have the highest delay or cost per shipment? |
| CRM | Head of Customer Success | Prevent churn, grow LTV | What is month-over-month retention by cohort? Who are the top-decile customers by rolling spend? |
| CX | Head of Customer Experience | Resolve issues fast, cut support cost | What is average resolution time by ticket category? Which order flags (returns, priority, coupon) correlate with ticket volume? |
| Product/Inventory | Head of Merchandising | Manage catalog health and stock risk | Which categories are trending up/down in monthly sales and rating? Where is stock at risk against demand? |

---

## 6. Data Sources (Bronze Layer)

| Source | Format | Key Contents | Notes / Known Complications |
|---|---|---|---|
| `raw_orders.parquet` | Parquet | order_id, customer_id, product_id, order datetime parts, qty/price/discount/tax/profit, payment method, shipping method, order status/priority, rating, fraud_risk_score | Pure transaction-fact extract; carries foreign keys only, not descriptive attributes |
| `raw_customer_master.csv` | CSV, Latin-1 | customer_id, name, gender, age, country, city, segment, loyalty_score, account_creation_date | Periodically refreshed master feed → source for SCD2 (segment upgrades, city changes) |
| `raw_product_catalog.json` | JSON | product_id, name, category, sub_category, brand, base price, rating, review count, stock | Versioned catalog snapshots → source for SCD2 (repricing, recategorization) |
| `raw_marketing.json` | JSON, nested | order_id, device_type, traffic_source, campaign_source, session_duration, pages_visited, abandoned_cart_before, coupon_used/code | Attribution data, one record per order session |
| `raw_returns.csv` | CSV | order_id, return_date, return_reason, refund_amount | Exists only for returned orders — partial coverage, arrives after the parent order (late-arriving fact) |
| `raw_support_tickets.json` | JSON | ticket_id, order_id, created_date, category, resolution_status, resolution_days | Exists only where a support ticket was raised — partial coverage, orphan-join risk against orders |

**Architectural rationale:** `raw_orders` is deliberately kept thin (FK-only) rather than denormalized with customer/product attributes, so the pipeline has to solve the real ETL problem of joining a fact to a dimension by natural key — including dimension members that haven't arrived yet (late-arriving dimensions) and facts with partial source coverage (returns, tickets).

---

## 7. Target Gold-Layer Bus Matrix

| Fact | Grain | Mart | Key Dimensions |
|---|---|---|---|
| `fct_order_line_financials` | 1 row per order line | Finance | Date, Customer, Product, Payment Method, Shipping Method, Order Flags (junk) |
| `fct_returns` | 1 row per returned line | Finance | Date, Customer, Product, Return Reason |
| `fct_web_attribution` | 1 row per order session | Marketing | Date, Customer, Channel (junk: campaign × traffic × device) |
| `fct_shipment` | 1 row per shipment | Logistics | Date, Warehouse, Shipping Method, Geography |
| `fct_support_ticket` | 1 row per ticket | CX | Date, Customer, Order (degenerate) |
| `fct_customer_monthly_snapshot` | 1 row per customer per month | CRM | Month, Customer |
| `fct_product_monthly_snapshot` | 1 row per product per month | Product/Inventory | Month, Product, Category |

**Conformed dimensions:** `dim_date`, `dim_customer` (SCD2), `dim_product` (SCD2), `dim_geography`, `dim_payment_method`, `dim_shipping_method`, `dim_channel` (junk: campaign_source × traffic_source × device_type, ~90 combinations), `dim_warehouse`, `dim_order_flags` (junk: is_weekend, installment_plan, coupon_used, abandoned_cart_before, order_priority).

`dim_customer` and `dim_product` are built via `dbt snapshot` against `raw_customer_master` / `raw_product_catalog` and carry full SCD2 history. All other dimensions are SCD Type 1 (overwrite) or junk/degenerate dimensions — re-deriving history for low-cardinality reference data is not warranted.

---

## 8. Functional Requirements

### 8.1 Data Governance
- Customer email and other PII fields must be normalized at staging; blanks populated with `'Unknown'`.
- Every transformation must be traceable through dbt lineage/docs.

### 8.2 Grain and Modeling Rules
- `fct_order_line_financials` is atomic: one row per order line item. No pre-aggregation before the Gold layer.
- `fct_customer_monthly_snapshot` and `fct_product_monthly_snapshot` are periodic snapshots at monthly grain.
- `dim_customer` and `dim_product` must be modeled as SCD Type 2 via dbt snapshot; all history-tracked attribute changes (segment, city, category, price) must be queryable as-of any date.
- `fct_returns` and `fct_support_ticket` are partial-coverage facts: the model must not assume every order has a matching return or ticket row, and must correctly resolve orders whose return/ticket record has not yet arrived (late-arriving fact handling) without dropping the parent order.
- Junk dimensions (`dim_channel`, `dim_order_flags`) must be built as pre-combined low-cardinality lookup tables, not joined as separate flag columns on the fact.

### 8.3 Reporting
- All Gold-layer facts and dimensions must be exposed to Power BI as a star schema per mart, with DAX measures covering the KPIs in Section 9.

---

## 9. Non-Functional Requirements

- **Compute:** Transformations run in-memory (DuckDB vectorized execution); no unnecessary disk spill.
- **Storage:** Staging (Bronze→Silver) and intermediate layers are materialized as views; only Gold-layer marts are materialized as physical tables.
- **Environment separation:** Local execution artifacts (DuckDB file, dbt target/) are excluded from version control via `.gitignore`.
- **Auditability:** Every Gold fact/dimension has dbt tests for primary key uniqueness, not-null, and referential integrity to conformed dimensions (with explicit tolerance for the partial-coverage facts in 8.2).

---

## 10. Success Criteria / CSFs and KPIs

| Domain | CSF | Example KPIs | Lead / Lag |
|---|---|---|---|
| Finance | Margin visibility including returns | Net margin %, return rate, refund cost as % of revenue | Lagging |
| Marketing | Channel efficiency | Conversion rate by channel, cart abandonment rate | Leading (abandonment) / Lagging (conversion) |
| Logistics | On-time, cost-efficient fulfilment | Avg shipping cost per order, on-time delivery rate | Lagging |
| CRM | Retention and LTV growth | Monthly retention rate by cohort, rolling 12-month spend | Lagging |
| CX | Fast, low-cost issue resolution | Avg resolution days, tickets per 100 orders | Leading (ticket volume) / Lagging (resolution time) |
| Product | Healthy, well-stocked catalog | Monthly category sales trend, stock-risk count | Leading |

Project delivery is considered successful when: all five sources ingest without manual intervention; all seven facts and their conformed dimensions pass dbt tests; SCD2 history is verifiably correct for at least one simulated attribute change per dimension; and each mart's Power BI page answers its stakeholder's core business questions from Section 5 using only Gold-layer tables.

---

## 11. Assumptions and Constraints

- Source data is a static Kaggle extract (`akrambelha/global-e-commerce-dataset-1m-records-20242026`); no live API exists, so "arrival" of late data is simulated by processing order rather than by real elapsed time.
- `fct_shipment` is derived from shipping-related fields already present in `raw_orders` (shipping method, cost, delivery status) rather than a dedicated shipment feed; `dim_warehouse` and `dim_geography` are derived/synthesized from customer country/city, as the source dataset has no explicit warehouse identifier. This should be validated once the underlying columns are confirmed.
- Volumes (~1M order rows) are assumed sufficient to produce meaningful partial-coverage and late-arrival scenarios for returns and tickets; if too sparse, synthetic augmentation may be needed.
- Single developer, local DuckDB environment — no concurrency or multi-user access requirements.

---

## 12. Glossary

- **SCD2 (Slowly Changing Dimension, Type 2):** A dimension modeling technique that preserves full history of attribute changes by adding new rows rather than overwriting.
- **Junk dimension:** A dimension combining several low-cardinality flags/attributes into one table to avoid many small dimension joins on the fact.
- **Degenerate dimension:** A dimension attribute (e.g., order_id) stored directly on the fact table with no separate dimension table.
- **Late-arriving fact:** A fact row (e.g., a return) that arrives in the source system after its related fact (the order) has already been loaded.
- **Conformed dimension:** A dimension shared and structurally identical across multiple data marts, enabling cross-mart analysis.
