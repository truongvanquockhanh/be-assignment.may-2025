# Justfile for Messaging API Backend Assignment
# Install Python dependencies
install: 
  pip install -r requirements.txt

# Run the FastAPI app
dev: 
  uvicorn app.main:app --reload

# Start services using Docker Compose
up: 
  docker-compose up db web

# Stop services
down: 
  docker-compose down

# Run database migrations (if using Alembic)
migrate: 
  alembic upgrade head
  
# Run tests
test:
  docker-compose up -d test-db
  until pg_isready -h localhost -p 5433 -U "testuser" -d "testdb"; do
    echo "Waiting for testdb to be ready..."
    sleep 1
  done
  source .env.test
  alembic upgrade head 
  PYTHONPATH=. pytest tests/test_messages.py
  PYTHONPATH=. pytest tests/test_users.py
  docker-compose down

# Format code using black and isort
format: 
  black .
  isort .

# Run the MCP server (optional)
mcp: 
  uvicorn app.mcp_server:app --reload
