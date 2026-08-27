# Business Requirements Document (BRD) 📑



\*\*Project Name:\*\* Amazon Marketplace Analytics Data Platform  

\*\*Document Owner:\*\* Sachintha KahaweWithana (Business Intelligence Specialist)  

\*\*Target Architecture:\*\* Modern Data Stack (Python + DuckDB + dbt Core)  



---



## 1. Executive Summary



### 1.1 Business Context

The modern e-commerce landscape requires data-driven decision-making to survive fast-changing market conditions and complex consumer behaviors. Operating as an enterprise-scale Amazon merchant vendor generates massive volumes of operational data across fragmented channels. Currently, business units are operating in siloed data environments, causing reporting delays and inconsistent business metrics across corporate dashboards.



### 1.2 Project Objective

The objective of this project is to centralize, clean, and model 1 Million rows of multi-format operational seller data. By replacing manual reporting with an automated, hybrid Medallion-Kimball Data Warehouse, this platform will provide a single version of truth across corporate operations, marketing attribution, and customer retention metrics.



---



## 2. Stakeholder Profiles \& Core Business Questions



The platform must ingest raw operational streams to answer the core strategic questions asked by individual business unit leads:



### 2.1 VP of Finance (Finance Mart)

\*   \*\*Objective:\*\* Optimize operating profit margins and audit transactional health.

\*   \*\*Core Business Questions:\*\*

&#x20;   \*   What is our true net revenue after stripping out local product cost price and tax liabilities?

&#x20;   \*   Which payment method experiences the highest failure rate, and what total capital is currently locked in a "pending" status?



### 2.2 Director of Growth Marketing (Marketing Mart)

\*   \*\*Objective:\*\* Maximize marketing budget efficiency and trace consumer web behavior.

\*   \*\*Core Business Questions:\*\*

&#x20;   \*   Which digital traffic acquisition channels yield the highest conversion rates to completed orders?

&#x20;   \*   Does consumer device type (Mobile vs. Desktop) heavily impact the total basket transaction size?



### 2.3 Head of Customer Success (CRM Mart)

\*   \*\*Objective:\*\* Prevent churn and drive historical customer lifetime values.

\*   \*\*Core Business Questions:\*\*

&#x20;   \*   What is our month-over-month customer retention rate broken down by historical registration cohorts?

&#x20;   \*   Who represents our top 1% "VIP" customer tier based on rolling annual spend velocities?



---



## 3. Data Scope \& System Constraints



The data warehouse is strictly bound by the boundaries of the upstream operational systems. The intake data ecosystem comprises three distinct source formats:



| Source File Component | Format | Technical Constraints / Known Anomaly States |

| :--- | :--- | :--- |

| \*\*Core Transactions\*\* | `.parquet` | High-velocity transaction logs. Must capture item-line granularity. |

| \*\*Customer Registries\*\* | `.csv` | Encoded in legacy text format (`Latin-1`). Contains missing strings (`NULL` records) and varying text spacing. |

| \*\*Web Clickstream\*\* | `.json` | Semi-structured payload. Contains deeply nested user browser and marketing campaign arrays. |



---



## 4. Functional Requirements



### 4.1 Data Governance & Security

\*   \*\*PII Sanitization:\*\* Customer email fields must be normalized, and any blank values must be populated with a standardized `'Unknown'` string placeholder during initial staging ingestion.

\*   \*\*Lineage Tracking:\*\* Every data transformation path must be fully traceable via dbt documentation to guarantee structural audibility.



### 4.2 Analytical Structural Rules (The Grain)

\*   \*\*Atomic Financials Grain:\*\* The transaction engine must model financials at the lowest granular layer: \*\*One row per individual order line item\*\*. Pre-aggregating data before the final data mart presentation layer is prohibited.

\*   \*\*Periodic CRM Snapshot Grain:\*\* Customer retention tracking must be aggregated on a \*\*Monthly Chronological Grain\*\* per customer to evaluate longitudinal cohort survival tracking.



---



## 5. Non-Functional Requirements



\*   \*\*Compute Efficiency:\*\* The pipeline transformations must run entirely in-memory using vectorized execution principles to minimize disk read/write bottlenecks.

\*   \*\*Storage Optimization:\*\* Ingestion layers (Staging) and connection bridges (Intermediate) must be built as lightweight logical views to prevent duplicate structural bloating of the physical local file storage.

\*   \*\*Environments Separation:\*\* Local analytics execution logic must remain fully decoupled from the stable production repository via a robust environment layout (`.gitignore`).



