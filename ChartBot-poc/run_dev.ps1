# Load environment variables
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

# Start ChromaDB if not running
if (!(docker ps --filter "name=chromadb" --format "{{.Names}}" | Select-String "chromadb")) {
    Write-Host "Starting ChromaDB..."
    docker run -d --name chromadb -p 8000:8000 `
        -e IS_PERSISTENT=TRUE `
        -e CHROMA_SERVER_HOST=0.0.0.0 `
        -e CHROMA_SERVER_HTTP_PORT=8000 `
        chromadb/chroma
    Start-Sleep -Seconds 5
}

# Start applications
Write-Host "Starting Chatbot..."
Set-Location chatbot
Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "app.main:app --host 0.0.0.0 --port 8001 --reload"

Write-Host "Starting Website..."
Set-Location ../website
Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "app.main:app --host 0.0.0.0 --port 8002 --reload"

Write-Host "✅ Applications are running:"
Write-Host "   Chatbot: http://localhost:8001"
Write-Host "   Website: http://localhost:8002"