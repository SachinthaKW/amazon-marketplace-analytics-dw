Welcome to your new dbt project!

### Dataset Structure

The Transaction Log (Parquet): A giant file (1M+ rows) of raw events or sales. DuckDB handles Parquet natively and lighting fast.

The Customer/User Registry (CSV): A messy file with mismatched date formats, missing fields, and bad encodings (like your Spotify error).

The Lookup/Category Metadata (JSON): Semi-structured nested data.

The Challenge: Force yourself to use DuckDB's unique parsing abilities (from_json, unnesting arrays) to clean this up in your dbt staging layer.

## Advanced dbt Concepts to Implement 

Incremental Models: Do not rebuild your massive transaction table from scratch every time. Change the dbt configuration to materialized='incremental' so it only appends new rows based on a timestamp lookback window.

Custom Macros (DRY Code): Don't repeat yourself. If you have a complex financial calculation (like converting currencies or calculating tax), write a reusable Jinja macro in your macros/ folder and call it across multiple models.

Custom Data Tests: Move beyond simple not_null tests. Write custom SQL tests in your tests/ folder to ensure complex business rules (e.g., “A refund date cannot occur before the original purchase date”).

## The DuckDB Power Moves

DuckDB has specific superpowers that standard cloud data warehouses don't. Showing you know how to use them proves you deep-dived the tool:MotherDuck Integration: Sign up for a free MotherDuck account (the cloud extension of DuckDB). Alter your profiles.yml so that dbt runs locally but pushes the final Marts tables up to a shared cloud instance.Spatial or Full-Text Extensions: Load a DuckDB extension (like spatial to calculate distances between delivery coordinates, or fts for searching text logs) directly inside a dbt macro.

## We will use Python's pandas library to split the dataset:

raw_orders.parquet: Holds order IDs, transaction values, and payment details (Simulating your main transactional system).

raw_customers.csv: Holds customer IDs, names, and emails. We will intentionally mess up the dates and encodings here to create the CSV chaos.

raw_marketing.json: Holds web traffic details like tracking codes and acquisition channels structured as nested JSON.