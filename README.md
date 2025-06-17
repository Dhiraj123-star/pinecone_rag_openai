
# 🌌 Pinecone RAG OpenAI API

Welcome to the **Pinecone RAG OpenAI API** project! 🚀  
This is a **FastAPI-based web application** that lets you store and search text using vector embeddings powered by **Pinecone** and **OpenAI**.  
Perfect for building **retrieval-augmented generation (RAG)** applications with ease! 😊

---

## 📌 Project Overview

This project provides a simple and intuitive API to:

- **Add Text 📝**: Store text data with embeddings in a Pinecone vector database.
- **Search Text 🔍**: Find similar texts based on a query using semantic search.
- **Reset Index 🧹**: Clear and reinitialize the Pinecone index for fresh starts.

It’s designed for developers and end-users who want to leverage AI-powered text search without complex setup. The API is **user-friendly**, **secure**, and runs **locally** with minimal configuration. 🌐

---

## ✨ Features

- **Text Storage**: Add multiple texts in a single request, automatically embedded with OpenAI's model. 📚  
- **Semantic Search**: Query texts and get the most similar results with similarity scores. 🧠  
- **Metadata Support**: Retrieve original texts alongside search results for context. 📜  
- **FastAPI Interface**: Interactive API documentation via Swagger UI for easy testing. 🖥️  
- **Secure Configuration**: Store API keys in a `.env` file for safety. 🔒  
- **Debugging Logs**: Detailed console logs for troubleshooting. 📈  

---

## 🛠️ Prerequisites

To run this project, you need:

- A **Pinecone account** with an API key (free plan supported). 🌲  
- An **OpenAI account** with an API key for embeddings. 🤖  
- **Python 3.12 or higher** installed. 🐍  
- A **local development environment** (e.g., Linux, macOS, or Windows). 💻  
- Basic knowledge of command-line tools and HTTP requests (e.g., curl or Postman). 🛠️  

---

## 🚀 Getting Started

### Clone the Repository 📂

Clone or download this project to your local machine.

---

### Set Up Virtual Environment 🧪

Navigate to the project directory.  
Create and activate a virtual environment:

- **Linux/macOS**:
  ```bash
  python -m venv venv && source venv/bin/activate
````

* **Windows**:

  ```bash
  python -m venv venv && venv\Scripts\activate
  ```

---

### Install Dependencies 📦

Install required packages using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### Configure Environment Variables 🔑

Create a `.env` file in the project root.
Add your Pinecone and OpenAI API keys:

```
PINECONE_API_KEY=your-pinecone-api-key
OPENAI_API_KEY=your-openai-api-key
```

Replace `your-pinecone-api-key` and `your-openai-api-key` with your actual keys.

---

### Run the API 🌐

Start the FastAPI server:

```bash
python main.py
```

The API will be available at:
[http://localhost:8000](http://localhost:8000)

---

### Explore the API 📖

Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to access the interactive Swagger UI.
Test the endpoints for adding and searching texts.

---

## 📚 How to Use

### 1. **Add Texts** (`POST /add`) 📝

* Send a list of texts to store in the Pinecone index.
* **Example**: `["The sun is bright today."]`
* **Response**: Confirms the number of texts added and their unique IDs.

---

### 2. **Search Texts** (`POST /search`) 🔎

* Send a query text and optional `top_k` (e.g., 3) to find similar texts.
* **Example**: `"What is the sky like?"`
* **Response**: Returns a list of matching texts, their IDs, and similarity scores.

---

### 3. **Reset Index** (`POST /reset-index`) 🧹

* Clears the Pinecone index and reloads sample data for testing.
* Useful for starting fresh or debugging.

---

Use tools like **curl**, **Postman**, or the **Swagger UI** to interact with these endpoints. 🛠️

---

## 🧪 Testing the API

### ✅ Add Sample Texts

Send a `POST` request to `/add` with a JSON body like:

```json
{"texts": ["Your text here"]}
```

Check the response for success and assigned IDs.

---

### 🔍 Search for Similar Texts

Send a `POST` request to `/search` with:

```json
{"query": "Your query", "top_k": 3}
```

Review the results to see matching texts and their similarity scores.

---

### 🧼 Reset for Fresh Start

Send a `POST` request to `/reset-index` to clear the index and reload sample data.

---

