import os
import shutil
import kagglehub
import pandas as pd

print("🚀 Step 1: Downloading the 1M Global E-Commerce dataset from Kaggle...")
raw_download_path = kagglehub.dataset_download(
    "akrambelha/global-e-commerce-dataset-1m-records-20242026")

# Find the downloaded file
csv_filename = None
for file in os.listdir(raw_download_path):
    if file.endswith('.csv'):
        csv_filename = os.path.join(raw_download_path, file)
        break

print(f"📦 Loading {csv_filename} into memory...")
# Load just 100 rows first to verify columns quickly
df = pd.read_csv(csv_filename, nrows=100)

print("\n🔍 DEBUG INFO: Here are the exact column names found in your dataset:")
print(list(df.columns))
print("-" * 50)

# Re-loading full dataset now that we know we can inspect columns
df = pd.read_csv(csv_filename)

# Standardise columns to lower_case with underscores to avoid human typo errors
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
print("✨ Standardised all column headers to lowercase with underscores!")

# Look at the list printed in your console to match these up.
# Based on common Kaggle structures, they will look like this:
order_cols = [col for col in ['order_id', 'customer_id', 'product_id',
                              'order_status', 'total_amount', 'payment_method'] if col in df.columns]
customer_cols = [col for col in ['customer_id', 'customer_name',
                                 'email', 'age', 'gender', 'country'] if col in df.columns]
marketing_cols = [col for col in ['order_id', 'traffic_source',
                                  'device_type', 'browser'] if col in df.columns]

# Backup safety net: If it still finds absolutely nothing, grab the first few columns
if len(order_cols) < 2:
    print("⚠️ Column names didn't match expectations. Defaulting to positional columns...")
    df.columns = [f"col_{i}" for i in range(len(df.columns))]
    df.rename(columns={"col_0": "order_id", "col_1": "customer_id",
              "col_2": "product_id"}, inplace=True)
    order_cols = ['order_id', 'customer_id', 'product_id']
    customer_cols = ['customer_id']
    marketing_cols = ['order_id']

# Ensure our target data folder exists
os.makedirs("data", exist_ok=True)

print("\n✂️ Step 2: Splitting the wide table into 3 messy source files...")

# --- SOURCE 1: TRANSACTIONS (Parquet) ---
orders_df = df[order_cols].copy()
orders_df.to_parquet("data/raw_orders.parquet", index=False)
print("  ✅ Saved data/raw_orders.parquet")

# --- SOURCE 2: CUSTOMERS (Messy CSV) ---
customers_df = df[customer_cols].copy()
if 'email' in customers_df.columns:
    customers_df.loc[customers_df.sample(frac=0.05).index, 'email'] = None
customers_df.to_csv("data/raw_customers.csv", index=False, encoding='latin1')
print("  ✅ Saved data/raw_customers.csv")

# --- SOURCE 3: MARKETING LOGS (Nested JSON) ---
marketing_df = df[marketing_cols].copy()
print("  ⚙️ Nesting marketing data fields into a JSON string structure...")

# Dynamically bundle whatever marketing columns were successfully found


def build_metadata(row):
    meta = {"traffic": {}}
    for col in marketing_cols:
        if col != 'order_id':
            meta["traffic"][col] = row[col]
    return meta


marketing_df['metadata'] = marketing_df.apply(build_metadata, axis=1)
final_json_df = marketing_df[['order_id', 'metadata']]
final_json_df.to_json("data/raw_marketing.json", orient="records", lines=True)
print("  ✅ Saved data/raw_marketing.json")

print("\n🎯 SUCCESS! Workspace populated.")
