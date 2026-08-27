\# Data Platform Architecture \& Blueprint 🏗️



This document details the system design, data flow topology, and data modeling boundaries of the Amazon Marketplace Analytics Platform.



\---



\## 1. The Kimball Enterprise Bus Matrix



The Bus Matrix defines the shared blueprint across our enterprise data assets. It cross-references business processes (which become transactional \*\*Fact Tables\*\*) against conformed dimensions (reusable \*\*Dimension Tables\*\*). This layout guarantees an absolute single version of truth across independent business units.



| Business Process (Fact Tables) | Dim Customers 👥 | Dim Products 📦 | Dim Web Attributes 🌐 | Dim Date 📅 |

| :--- | :---: | :---: | :---: | :---: |

| \*\*Order Financials\*\* \*(Finance Mart)\* | \*\*X\*\* | \*\*X\*\* | | \*\*X\*\* |

| \*\*Web Sessions\*\* \*(Marketing Mart)\* | \*\*X\*\* | | \*\*X\*\* | \*\*X\*\* |

| \*\*Customer Retention\*\* \*(CRM Mart)\* | \*\*X\*\* | | | \*\*X\*\* |



\*Architectural Rule:\* `Dim Customers` and `Dim Date` are \*\*Conformed Dimensions\*\*. They share the exact same structural keys across all downstream Data Marts to prevent data discrepancy between departments.



\---



\## 2. Data Flow Diagram (DFD)



The platform follows a strict, non-skipping \*\*Medallion Architecture (Bronze → Silver → Gold)\*\*. Data moves sequentially through layers to transition from raw operational storage to highly optimized dimensional schemas.



```mermaid

graph TD
    %% Define Styles
    classDef bronze fill:#f9cb9c,stroke:#e69138,stroke-width:2px,color:#000;
    classDef silver fill:#cfe2f3,stroke:#3d85c6,stroke-width:2px,color:#000;
    classDef gold fill:#ffe599,stroke:#f1c232,stroke-width:2px,color:#000;
    classDef bi fill:#d9ead3,stroke:#6aa84f,stroke-width:2px,color:#000;

    %% Bronze Layer
    subgraph BRONZE [Bronze Layer: Raw Source Files]
        A[raw_orders.parquet]:::bronze
        B[raw_customers.csv]:::bronze
        C[raw_marketing.json]:::bronze
    end

    %% Silver Layer - Staging
    subgraph SILVER_STG [Silver Layer: Staging Views]
        stg_O[stg_orders]:::silver
        stg_C[stg_customers]:::silver
        stg_M[stg_marketing]:::silver
    end

    %% Silver Layer - Intermediate
    subgraph SILVER_INT [Silver Layer: Intermediate Processing]
        int_F[int_finance_transform]:::silver
        int_M[int_marketing_transform]:::silver
        int_R[int_crm_retention_transform]:::silver
    end

    %% Gold Layer - Data Marts
    subgraph GOLD [Gold Layer: Kimball Star Schema Data Marts]
        
        subgraph FINANCE_MART [Finance Mart]
            F1[fct_order_financials]:::gold
            D1[dim_products]:::gold
        end
        
        subgraph MARKETING_MART [Marketing Mart]
            F2[fct_web_sessions]:::gold
            D2[dim_web_attributes]:::gold
        end
        
        subgraph CRM_MART [CRM Mart]
            F3[fct_customer_retention]:::gold
            D3[dim_customers]:::gold
        end
    end

    %% Consumer Layer
    Dash[Power BI / Tableau Dashboards]:::bi

    %% 1. Ingestion Links
    A --> stg_O
    B --> stg_C
    C --> stg_M

    %% 2. Transformation Pipelines (Isolated Channels)
    stg_O --> int_F
    
    stg_M --> int_M
    stg_O --> int_M
    
    stg_C --> int_R
    stg_O --> int_R

    %% 3. Materializing Facts
    int_F --> F1
    int_M --> F2
    int_R --> F3

    %% 4. Materializing Dimensions
    stg_O --> D1
    stg_M --> D2
    stg_C --> D3

    %% 5. Star Schema Relational Joins (The Kimball Keys)
    D1 -.->|Product FK| F1
    D3 -.->|Customer FK| F1
    D2 -.->|Web Attr FK| F2
    D3 -.->|Customer FK| F2
    D3 -.->|Customer FK| F3

    %% 6. Final Dashboard Outputs
    F1 --> Dash
    F2 --> Dash
    F3 --> Dash
```





\---



\## 3. Layer Processing Definitions



\### 🥈 Silver Staging Layer (Atomic Views)

\*   \*\*Materialization:\*\* `view`

\*   \*\*Rule:\*\* 1:1 structural copy of the raw source file. No multi-table combinations are allowed.

\*   \*\*Transformations:\*\* Enforces strong data type casting, converts text strings to standard ISO dates, handles missing strings using `COALESCE`, and normalizes column headers to lowercase underscores.



\### 🥈 Silver Intermediate Layer (Consolidated Logic)

\*   \*\*Materialization:\*\* `view`

\*   \*\*Rule:\*\* Aggregates and links raw identifiers. 

\*   \*\*Transformations:\*\* Resolves table boundaries using left joins across staging views to establish relational links before data mart delivery.



\### 🥇 Gold Presentation Layer (Target Data Marts)

\*   \*\*Materialization:\*\* `table`

\*   \*\*Rule:\*\* Structured explicitly using Kimball Star Schema design principles (Facts and Dimensions).

\*   \*\*Transformations:\*\* Computes business KPIs (Net profit margins, retention spans, conversion metrics) materialized physically to local storage blocks for peak BI reporting speed.



