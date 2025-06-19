# 🌌 Pinecone RAG OpenAI API

Welcome to the Pinecone RAG OpenAI API project! 🚀 This is a FastAPI-based web application that lets you store and search text using vector embeddings powered by Pinecone and OpenAI. Perfect for building retrieval-augmented generation (RAG) applications with ease! 😊

## 📌 Project Overview

This project provides a secure and efficient API to:

- **Add Text 📝**: Store text data with embeddings in a Pinecone vector database, tagged with user-specific metadata.  
- **Search Text 🔍**: Find similar texts based on a query using semantic search, filtered by user.  
- **User Authentication 🔐**: Secure endpoints with JWT-based authentication for user-specific access.  
- **Health Monitoring 🩺**: Check API status with a dedicated health endpoint.  
- **Reset Index 🧹**: Clear and reinitialize the Pinecone index for fresh starts.  

It’s designed for developers building RAG applications, offering secure, scalable, and production-ready functionality with minimal setup. The API is deployable locally or via Docker, with automated CI/CD to Docker Hub. 🌐

## ✨ Features

- **Text Storage**: Add multiple texts in a single request, automatically embedded with OpenAI's model and linked to authenticated users. 📚  
- **Semantic Search**: Query texts and get user-specific similar results with similarity scores. 🧠  
- **Metadata Support**: Retrieve original texts alongside search results for context. 📜  
- **JWT Authentication**: Secure /add and /search endpoints with user-specific JWTs via a /login endpoint. 🔒  
- **Health Checks**: Monitor API availability with a public /health endpoint for Docker and external tools. 🩺  
- **FastAPI Interface**: Interactive API documentation via Swagger UI for easy testing. 🖥️  
- **Secure Configuration**: Store sensitive keys (Pinecone, OpenAI, JWT) in a .env file. 🔑  
- **Production-Ready**: Run with multiple Uvicorn workers for high performance and scalability. ⚙️  
- **CI/CD Pipeline**: Automate building and deploying Docker images to dhiraj918106/pinecone_rag_openai using GitHub Actions. 🚀  
- **Dockerized Deployment**: Run locally or pull from Docker Hub with Docker Compose for easy setup. 🐳  
- **Debugging Logs**: Detailed console logs for troubleshooting. 📈  

## 🛠️ Prerequisites

To run this project, you need:

- A Pinecone account with an API key (free plan supported). 🌲  
- An OpenAI account with an API key for embeddings. 🤖  
- Python 3.12 or higher installed (for local development). 🐍  
- Docker and Docker Compose for containerized deployment. 🐳  
- A Docker Hub account to pull the image (dhiraj918106/pinecone_rag_openai). 📦  
- A GitHub repository with Actions enabled for CI/CD. 🛠️  
- A local development environment (e.g., Linux, macOS, or Windows). 💻  
- Basic knowledge of command-line tools and HTTP requests (e.g., curl or Postman). 🛠️  
