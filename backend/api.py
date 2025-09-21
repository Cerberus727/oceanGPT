# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

# --- 1. SETUP & CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD", "YOUR_POSTGRES_PASSWORD")

# --- NEW: INITIALIZE VECTOR DB AND EMBEDDING MODEL ON STARTUP ---
try:
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    collection = chroma_client.get_collection(name="argo_float_summaries")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ ChromaDB and sentence-transformer model loaded successfully.")
except Exception as e:
    print(f"❌ ERROR: Could not load ChromaDB. Run populate_vectordb.py first. Error: {e}")
    collection = None
    embedding_model = None
# --- END OF NEW SECTION ---

app = FastAPI(
    title="OceanGPT API",
    description="API for querying ARGO float data using natural language.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DATABASE CONNECTION ---
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'argo_db'
engine_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(engine_string)

def run_query(query_string: str) -> pd.DataFrame:
    """Executes a SQL query and returns the result as a pandas DataFrame."""
    return pd.read_sql(text(query_string), engine.connect())

# --- 3. ADVANCED AI CONTEXT (Copied directly from your final app.py) ---
def get_db_context():
    """Fetches schema, date range, and unique floats to give the AI better context."""
    schema_query = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'argo_data'"
    date_range_query = "SELECT MIN(juld)::date AS min_date, MAX(juld)::date AS max_date FROM argo_data;"
    platform_query = "SELECT DISTINCT platform_number FROM argo_data ORDER BY platform_number;"
    
    schema_df = run_query(schema_query)
    date_range_df = run_query(date_range_query)
    platform_df = run_query(platform_query)

    schema_info = "\n".join([f"- {row['column_name']} ({row['data_type']})" for _, row in schema_df.iterrows()])
    date_range_info = f"The data covers dates from {date_range_df['min_date'][0]} to {date_range_df['max_date'][0]}."
    platform_info = "Available platform_number values include: " + ", ".join(platform_df['platform_number'].astype(str).tolist()[:10]) + ", among others."

    full_context = f"""
    You are querying a PostgreSQL table named 'argo_data' with the following schema:
    {schema_info}

    Contextual Information:
    - {date_range_info}
    - {platform_info}
    """
    return full_context

DB_CONTEXT = get_db_context()

# --- 4. RAG PIPELINE LOGIC ---

# --- NEW: FUNCTION TO SEARCH THE VECTOR DB ---
def find_relevant_context(user_question: str) -> str:
    """Searches the vector DB for context relevant to the user's question."""
    if not collection or not embedding_model:
        return "Vector database not available."
    
    query_embedding = embedding_model.encode(user_question).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    context = "\n---\n".join(results['documents'][0])
    return context
# --- END OF NEW SECTION ---

def get_sql_query(user_question: str, context: str) -> str:
    """Converts a user question to a SQL query, using the perfected prompt and new context."""
    # This is the perfected prompt, now with a placeholder for the retrieved context.
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are an expert PostgreSQL query writer. Your task is to convert a user's question into a single, syntactically correct SQL query. "
             "Use the provided **retrieved context** and **database context** to help you write the most accurate query.\n\n"
             "--- RETRIEVED CONTEXT (from vector search) ---\n{context}\n--------------------------------------------\n\n"
             "Follow these rules precisely:\n"
             "1. **For 'highest'/'lowest'/'latest' records (e.g., 'furthest south'), ALWAYS use `ORDER BY` and `LIMIT 1`.** DO NOT use `GROUP BY`. "
             "   - 'Furthest south' means `ORDER BY latitude ASC LIMIT 1`. 'Furthest west' means `ORDER BY longitude ASC LIMIT 1`.\n"
             "2. **For aggregates on a 'top N' subset, ALWAYS use a subquery.**\n"
             "3. **ALWAYS use descriptive aliases for aggregate columns** (e.g., `AVG(temperature) AS average_temperature`).\n"
             "4. **Interpret geographical terms**: 'equator' means `latitude BETWEEN -5 AND 5`.\n"
             "5. **Always include columns mentioned by the user.** If asked 'Which float...', you must select `platform_number`.\n"
             "6. Only output the SQL query. Nothing else.\n\n"
             "--- DATABASE CONTEXT ---\n{db_context}\n-------------------------"
            ),
            ("human", "{question}")
        ]
    )
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
    chain = prompt | llm
    response = chain.invoke({"question": user_question, "context": context, "db_context": DB_CONTEXT})
    sql_query = response.content.strip().replace("```sql", "").replace("```", "")
    return sql_query

def get_natural_language_summary(question: str, results_df: pd.DataFrame) -> str:
    """Generates a natural language summary of the query results."""
    if results_df.empty:
        return "I couldn't find any data that matches your query. Please try asking in a different way."
    
    results_str = results_df.to_markdown(index=False)
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful oceanographic data analyst. The user asked: '{question}'. "
        "The following data was retrieved from the database:\n{results}\n\n"
        "Please provide a concise, natural language summary of the findings."
    )
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
    chain = prompt | llm
    response = chain.invoke({"question": question, "results": results_str})
    return response.content

# --- 5. API ENDPOINT (Updated to use RAG) ---
class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    """The main API endpoint that now uses the RAG pipeline."""
    try:
        # Step 1 (Retrieve): Find relevant context from the vector DB
        context = find_relevant_context(request.question)
        
        # Step 2 (Augment & Generate): Create the SQL query using the new context and our perfected prompt
        sql_query = get_sql_query(request.question, context)
        
        # Step 3: Execute the query
        results_df = run_query(sql_query)
        
        # Step 4: Generate a natural language summary
        summary = get_natural_language_summary(request.question, results_df)
        
        # Convert data for JSON
        for col in results_df.select_dtypes(include=['datetime64[ns]']).columns:
            results_df[col] = results_df[col].astype(str)
        for col in results_df.columns:
             if pd.api.types.is_numeric_dtype(results_df[col].dtype):
                 results_df[col] = results_df[col].apply(lambda x: float(x) if isinstance(x, np.number) else x)
        results_json = results_df.to_dict(orient='records')
        
        return {
            "summary": summary,
            "data": results_json,
            "sql_query": sql_query,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))