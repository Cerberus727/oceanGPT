# load_to_sql.py

import pandas as pd
from sqlalchemy import create_engine

# --- DATABASE CONNECTION DETAILS ---
# IMPORTANT: Replace with your own PostgreSQL credentials
db_user = 'postgres'
db_password = '123456' # The password you set during installation
db_host = 'localhost'
db_port = '5432'
db_name = 'argo_db'

# --- The name of our data table ---
table_name = 'argo_data'

# --- Path to our data file ---
parquet_file = 'argo_final_data.parquet'

print(f"Reading data from {parquet_file}...")
df = pd.read_parquet(parquet_file)

# The 'platform_number' column was read as a binary object, let's decode it
# This is a common step when moving from certain file formats
if 'platform_number' in df.columns and df['platform_number'].dtype == 'object':
    # Check if the column contains bytes and decode
    if isinstance(df['platform_number'].iloc[0], bytes):
        df['platform_number'] = df['platform_number'].str.decode('utf-8')


print(f"Successfully loaded {len(df)} rows.")

# Create the connection string for SQLAlchemy
engine_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(engine_string)

print(f"Connecting to database '{db_name}' and loading data into table '{table_name}'...")

# Use df.to_sql to load the data
# if_exists='replace': Deletes the old table and creates a new one. Good for re-running the script.
# chunksize: Loads data in batches of 1000 rows to avoid using too much memory.
df.to_sql(
    table_name,
    con=engine,
    if_exists='replace',
    index=False,
    chunksize=1000
)

print("SUCCESS: Data has been loaded into the PostgreSQL database.")