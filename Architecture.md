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

&#x20;   %% Define Styles

&#x20;   classDef bronze fill:#f9cb9c,stroke:#e69138,stroke-width:2px,color:#000;

&#x20;   classDef silver fill:#cfe2f3,stroke:#3d85c6,stroke-width:2px,color:#000;

&#x20;   classDef gold fill:#ffe599,stroke:#f1c232,stroke-width:2px,color:#000;

&#x20;   classDef bi fill:#d9ead3,stroke:#6aa84f,stroke-width:2px,color:#000;



&#x20;   %% Bronze Layer

&#x20;   subgraph BRONZE \[Bronze Layer: Raw Source Files]

&#x20;       A\[raw\_orders.parquet]:::bronze

&#x20;       B\[raw\_customers.csv]:::bronze

&#x20;       C\[raw\_marketing.json]:::bronze

&#x20;   end



&#x20;   %% Silver Layer - Staging

&#x20;   subgraph SILVER\_STG \[Silver Layer: Staging Views]

&#x20;       stg\_O\[stg\_orders]:::silver

&#x20;       stg\_C\[stg\_customers]:::silver

&#x20;       stg\_M\[stg\_marketing]:::silver

&#x20;   end



&#x20;   %% Silver Layer - Intermediate

&#x20;   subgraph SILVER\_INT \[Silver Layer: Intermediate Processing]

&#x20;       int\_O\[int\_order\_details]:::silver

&#x20;   end



&#x20;   %% Gold Layer - Data Marts

&#x20;   subgraph GOLD \[Gold Layer: Kimball Star Schema Data Marts]

&#x20;       direction TB

&#x20;       subgraph FINANCE\_MART \[Finance Mart]

&#x20;           F1\[fct\_order\_financials]:::gold

&#x20;           D1\[dim\_products]:::gold

&#x20;       end

&#x20;       subgraph MARKETING\_MART \[Marketing Mart]

&#x20;           F2\[fct\_web\_sessions]:::gold

&#x20;           D2\[dim\_web\_attributes]:::gold

&#x20;       end

&#x20;       subgraph CRM\_MART \[CRM Mart]

&#x20;           F3\[fct\_customer\_retention]:::gold

&#x20;           D3\[dim\_customers]:::gold

&#x20;       end

&#x20;   end



&#x20;   %% Consumer Layer

&#x20;   subgraph BI \[Reporting \& Consumption]

&#x20;       Dash\[Power BI / Tableau Executive Dashboards]:::bi

&#x20;   end



    %% Data Pipeline Relationships
    A --> stg_O
    B --> stg_C
    C --> stg_M

    stg_O --> int_O
    stg_C --> int_O
    stg_M --> int_O

    int_O --> F1
    int_O --> F2
    int_O --> F3
    
    stg_C --> D3
    stg_M --> D2

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



