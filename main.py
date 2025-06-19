import os
import time
import uuid
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Security, Depends, Header
from pydantic import BaseModel
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

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
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not PINECONE_API_KEY or not OPENAI_API_KEY or not JWT_SECRET_KEY or not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise ValueError("PINECONE_API_KEY, OPENAI_API_KEY, JWT_SECRET_KEY, ADMIN_USERNAME, and ADMIN_PASSWORD must be set in .env file")

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

# JWT configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# In-memory user store (for simplicity, single admin user)
users_db = {
    ADMIN_USERNAME: {
        "username": ADMIN_USERNAME,
        "hashed_password": pwd_context.hash(ADMIN_PASSWORD),
        "user_id": str(uuid.uuid4())  # Unique user ID
    }
}

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

class Token(BaseModel):
    access_token: str
    token_type: str

# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to get user from in-memory db
def get_user(username: str):
    return users_db.get(username)

# Function to authenticate user
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

# Function to create JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get current user from JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

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
def upsert_data(texts: List[str], ids: List[str], user_id: str) -> Dict:
    try:
        embeddings = [get_embedding(text) for text in texts]
        if None in embeddings:
            raise ValueError("One or more embeddings failed to generate")
        vectors = [
            {"id": str(id), "values": emb, "metadata": {"text": text, "user_id": user_id}}
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
def query_pinecone(query_text: str, top_k: int, user_id: str) -> List[Dict]:
    query_embedding = get_embedding(query_text)
    if query_embedding is None:
        raise HTTPException(status_code=500, detail="Query embedding failed")
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"user_id": user_id}
    )
    print("Raw query result:", result)
    return [
        {
            "id": match["id"],
            "score": match["score"],
            "text": match.get("metadata", {}).get("text", "N/A")
        }
        for match in result["matches"]
    ]

# API endpoint to login and get JWT
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["user_id"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# API endpoint to add texts
@app.post("/add", response_model=Dict)
async def add_texts(request: AddTextRequest, current_user: dict = Depends(get_current_user)):
    """
    Add texts to the Pinecone index with embeddings.
    """
    if not request.texts:
        raise HTTPException(status_code=400, detail="At least one text is required")
    
    # Generate unique IDs for each text
    ids = [str(uuid.uuid4()) for _ in request.texts]
    
    # Upsert texts with user_id
    response = upsert_data(request.texts, ids, current_user["user_id"])
    time.sleep(2)  # Wait for index to update
    return {
        "message": "Texts added successfully",
        "upserted_count": response.get("upserted_count", 0),
        "ids": ids
    }

# API endpoint to search texts
@app.post("/search", response_model=List[SearchResult])
async def search_texts(request: SearchTextRequest, current_user: dict = Depends(get_current_user)):
    """
    Search for similar texts in the Pinecone index.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty")
    
    # Query Pinecone with user_id filter
    matches = query_pinecone(request.query, request.top_k, current_user["user_id"])
    return matches

# API endpoint for health check
@app.get("/health")
async def health_check():
    """
    Check the health of the API.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)