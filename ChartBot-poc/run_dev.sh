#!/bin/bash

# Load environment variables
source .env

# Start ChromaDB if not running
if ! docker ps | grep -q chromadb; then
    echo "Starting ChromaDB..."
    docker run -d --name chromadb -p 8000:8000 \
        -e IS_PERSISTENT=TRUE \
        -e CHROMA_SERVER_HOST=0.0.0.0 \
        -e CHROMA_SERVER_HTTP_PORT=8000 \
        chromadb/chroma
    sleep 5
fi

# Start applications in background
echo "Starting Chatbot..."
cd chatbot
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &

echo "Starting Website..."
cd ../website
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload &

echo "✅ Applications are running:"
echo "   Chatbot: http://localhost:8001"
echo "   Website: http://localhost:8002"
echo "   Press Ctrl+C to stop all services"

# Wait for Ctrl+C
wait