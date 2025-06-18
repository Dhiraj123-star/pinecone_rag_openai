import os
import time
import uuid
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from dotenv import load_dotenv

# Initialize FastAPI app
app = FastAPI(
    title="Pinecone RAG API",
    description="API to add and search text using Pinecone and OpenAI embeddings",
    version="1.0.0"
)

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone client
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    raise ValueError("PINECONE_API_KEY and OPENAI_API_KEY must be set in .env file")

pc = Pinecone(api_key=PINECONE_API_KEY)

# Define index name and parameters
INDEX_NAME = "rag-index"
DIMENSION = 1536
METRIC = "cosine"
CLOUD = "aws"
REGION = "us-east-1"  # Free plan supported region

# Delete existing index to start fresh (optional, comment out if not needed)
try:
    pc.delete_index(INDEX_NAME)
    print(f"Deleted existing index: {INDEX_NAME}")
except Exception as e:
    print(f"No existing index to delete or error: {str(e)}")

# Create or connect to Pinecone index
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(
            cloud=CLOUD,
            region=REGION
        )
    )
    print(f"Created new index: {INDEX_NAME}")

# Connect to the index
index = pc.Index(INDEX_NAME)

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Pydantic models for request validation
class AddTextRequest(BaseModel):
    texts: List[str]

class SearchTextRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    id: str
    score: float
    text: str

# Function to generate embeddings
def get_embedding(text: str) -> List[float]:
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding
        print(f"Embedding for '{text}': length={len(embedding)}, first few values={embedding[:5]}")
        return embedding
    except Exception as e:
        print("Embedding error:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")

# Function to upsert data with metadata
def upsert_data(texts: List[str], ids: List[str]) -> Dict:
    try:
        embeddings = [get_embedding(text) for text in texts]
        if None in embeddings:
            raise ValueError("One or more embeddings failed to generate")
        vectors = [
            {"id": str(id), "values": emb, "metadata": {"text": text}}
            for id, emb, text in zip(ids, embeddings, texts)
        ]
        response = index.upsert(vectors=vectors)
        print("Upsert response:", response)
        print("Index stats after upsert:", index.describe_index_stats())
        return response
    except Exception as e:
        print("Upsert failed:", str(e))
        raise HTTPException(status_code=500, detail=f"Upsert failed: {str(e)}")

# Function to query Pinecone with metadata
def query_pinecone(query_text: str, top_k: int) -> List[Dict]:
    query_embedding = get_embedding(query_text)
    if query_embedding is None:
        raise HTTPException(status_code=500, detail="Query embedding failed")
    result = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    print("Raw query result:", result)
    return [
        {
            "id": match["id"],
            "score": match["score"],
            "text": match.get("metadata", {}).get("text", "N/A")
        }
        for match in result["matches"]
    ]

# API endpoint to add texts
@app.post("/add", response_model=Dict)
async def add_texts(request: AddTextRequest):
    """
    Add texts to the Pinecone index with embeddings.
    """
    if not request.texts:
        raise HTTPException(status_code=400, detail="At least one text is required")
    
    # Generate unique IDs for each text
    ids = [str(uuid.uuid4()) for _ in request.texts]
    
    # Upsert texts
    response = upsert_data(request.texts, ids)
    time.sleep(2)  # Wait for index to update
    return {
        "message": "Texts added successfully",
        "upserted_count": response.get("upserted_count", 0),
        "ids": ids
    }

# API endpoint to search texts
@app.post("/search", response_model=List[SearchResult])
async def search_texts(request: SearchTextRequest):
    """
    Search for similar texts in the Pinecone index.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty")
    
    # Query Pinecone
    matches = query_pinecone(request.query, request.top_k)
    return matches

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)