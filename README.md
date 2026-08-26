# Amazon Marketplace Analytics Data Platform 🚀

An enterprise-scale data platform engineered to ingest, clean, and model multi-source Amazon seller metrics and consumer clickstream logs. This project simulates a real-world modern data stack (MDS) architecture, utilizing **dbt Core** and **DuckDB** to transform over 1 Million rows of raw operational data into a high-performance analytical warehouse structured under Kimball Star Schema design principles.

---

## 🏗️ Architecture Overview

The platform is designed around the **Medallion (Bronze/Silver/Gold) Architecture**, enforcing a strict separation of concerns between raw file storage, data transformation logic, and downstream business intelligence (BI) consumption.

```text
   [ MULTI-SOURCE CHAOS ]      [ BRONZE ] ───► [ SILVER ] ───► [ GOLD LAYER ]
  
  📦 Transactions (Parquet)  ───────┐
  📄 Customer Ops (CSV)      ───────┼───►  🥈 STAGING (Views)
  🌐 Clickstream (JSON)      ───────┘           │
                                                ▼
                                           🥈 INTERMEDIATE (Views)
                                                │
                                                ▼
                                           🥇 MARTS (Physical Tables)
                                                │
                                                ▼
                                           📊 BI Dashboards & Users

```

### Engineered Data Chaos (Multi-Format Ingestion)
To simulate production-grade data ecosystem challenges, a single wide upstream transaction matrix of **1,000,000+ rows** was programmatically deconstructed into three distinct, decoupled source environments using Python:
1. **Core Transactions (`.parquet`):** Dense, columnar binary blocks representing high-velocity, fast-moving order logs.
2. **Customer Registries (`.csv`):** Messy operational files embedded with intentional data anomalies, missing fields (`NULL` strings), and complex legacy text encodings (`Latin-1`).
3. **Web Session Telemetry (`.json`):** Semi-structured, deeply nested JSON objects tracking multi-device consumer traffic sources and browser attributes.

---

## 🛠️ Tech Stack & Key Superpowers

* **Data Transformation:** `dbt-core (v1.12+)` for modular modular pipeline orchestration, lineage tracking, and compiler testing.
* **Storage & Compute Engine:** `DuckDB (v1.11+)` utilizing vectorised execution to parse and query local Parquet, CSV, and JSON structures natively at lightning speeds.
* **Automation:** `Python 3.13` + `Pandas` + `PyArrow` + `Kagglehub` for programmatic data collection and automated schema splitting.
* **Version Control:** `Git` / `GitHub` for strict repository asset tracking.

---

## 📂 Repository Structure

```text
amazon-marketplace-analytics-dw/
├── .gitignore                     # Prevents tracking of heavy local binaries (.duckdb) and data directories
├── generate_chaos.py              # Automated script extracting and breaking raw datasets into multiple file formats
├── README.md                      # Platform documentation
├── data/                          # HIDE FROM GIT: Dedicated storage directory for local raw files
│   ├── raw_orders.parquet
│   ├── raw_customers.csv
│   └── raw_marketing.json
└── my_duckdb_project/            # The standalone dbt core project
    ├── dbt_project.yml            # Pipeline master configurations
    ├── profiles.yml               # Connection configuration pointing to local analytical DuckDB files
    ├── macros/                    # Reusable SQL calculations written in Jinja
    └── models/
        ├── staging/               # Silver Layer: Normalised views casting data types, fixing text encoding
        ├── intermediate/          # Silver Transition: Joins across sources, heavy data deduplication
        └── marts/                 # Gold Layer: Physical fact/dimension tables optimised for BI reporting
```

---

## 🚀 Execution & Quick Start

### 1. Prerequisites
Ensure you have Python installed and your virtual environment active:
```powershell
# Activate your local development sandbox
.venv\Scripts\Activate.ps1
```

### 2. Generate the Source Environment
Run the data pipeline loader script to fetch the 1-Million row dataset from Kaggle, execute the multi-source architectural split, and automatically build your local `data/` workspace:
```powershell
python generate_chaos.py
```

### 3. Initialize and Run the dbt Framework
Navigate into the dbt core engine workspace, verify your environment hooks pass debugging checks, and execute the full analytics pipeline transformations:
```powershell
cd my_duckdb_project
dbt debug
dbt run
```

---

## 🎯 Analytical Competence Milestones Met

* **DuckDB Ingestion Engine:** Successfully weaponized DuckDB's unique `read_parquet()`, `read_csv_auto(encoding='latin1')`, and `json_extract_text()` parsing syntax to pipeline multi-format files smoothly inside a pure SQL workflow.
* **Defensive Data Modelling:** Enforced `COALESCE` string treatments over corrupted or omitted records in the staging layer to maintain absolute relational integrity before downstream grouping.
* **Kimball Star Schema Transformation:** Restructured chaotic operational columns into clean reporting formats, decoupling data into high-value transactional metrics and robust user descriptive components ready to power automated dashboards.

---

## 👤 Author

* **Sachintha KahaweWithana** - Business Intelligence Specialist
* **Location:** Auckland, New Zealand
* **LinkedIn:** [://linkedin.com](https://www.://linkedin.com)
