import pandas as pd
from sqlalchemy import create_engine, text
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from tqdm import tqdm

print("--- Starting Vector Database Population Process ---")

# --- 1. Load Configuration ---
load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD", "YOUR_POSTGRES_PASSWORD")
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'argo_db'

# --- 2. Connect to PostgreSQL ---
print("Connecting to PostgreSQL to fetch float summary data...")
try:
    engine_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(engine_string)
    
    # Query to get a summary for each unique float
    summary_query = """
    SELECT 
        platform_number,
        COUNT(DISTINCT cycle_number) as total_cycles,
        MIN(juld)::date as first_seen,
        MAX(juld)::date as last_seen,
        MIN(latitude) as min_lat,
        MAX(latitude) as max_lat,
        MIN(longitude) as min_lon,
        MAX(longitude) as max_lon
    FROM 
        argo_data
    GROUP BY 
        platform_number
    ORDER BY
        platform_number;
    """
    floats_df = pd.read_sql(text(summary_query), engine.connect())
    print(f"Successfully fetched summary data for {len(floats_df)} unique floats.")

except Exception as e:
    print(f"❌ ERROR: Could not connect to PostgreSQL. Please check your connection details. Error: {e}")
    exit()

# --- 3. Generate Text Summaries (Documents) ---
print("Generating text summaries for each float...")
documents = []
metadatas = []
ids = []

for _, row in tqdm(floats_df.iterrows(), total=floats_df.shape[0], desc="Processing floats"):
    # Create a simple, descriptive sentence for each float
    doc = (
        f"ARGO float with platform number {row['platform_number']} was active from {row['first_seen']} to {row['last_seen']}. "
        f"It recorded {row['total_cycles']} cycles. "
        f"Its operational area was between latitudes {row['min_lat']:.2f} and {row['max_lat']:.2f}, and longitudes {row['min_lon']:.2f} and {row['max_lon']:.2f}."
    )
    documents.append(doc)
    # Store the platform number in the metadata for easy retrieval
    metadatas.append({"platform_number": str(row['platform_number'])})
    # Use the platform number as the unique ID for each entry
    ids.append(str(row['platform_number']))

# --- 4. Create Vector Embeddings ---
# This will download a pre-trained model from Hugging Face the first time it's run
print("Loading sentence-transformer model to create vector embeddings...")
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(documents, show_progress_bar=True)
print("Embeddings created successfully.")

# --- 5. Initialize ChromaDB and Populate the Collection ---
print("Initializing ChromaDB client...")
# This creates a persistent database in a folder named 'chroma_db'
client = chromadb.PersistentClient(path="chroma_db") 

# Create a new collection or get it if it already exists
collection_name = "argo_float_summaries"
print(f"Creating or getting ChromaDB collection: '{collection_name}'")
collection = client.get_or_create_collection(name=collection_name)

# Add the documents, embeddings, and metadata to the collection
# This process might take a moment
print("Adding data to the ChromaDB collection. This may take a few minutes...")
collection.add(
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print("\n--- ✅ Vector Database Population Complete! ---")
print(f"A new folder named 'chroma_db' has been created in your project directory.")
print(f"The collection '{collection_name}' now contains {collection.count()} entries.")