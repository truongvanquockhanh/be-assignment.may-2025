# Justfile for Messaging API Backend Assignment

CURRENT*TIMESTAMP:=`date +'%Y%m%d*%H:%M:%S'`

# Install Python dependencies

install:
pip install -r requirements.txt

# Run the FastAPI app

dev:
uvicorn app.main:app --reload

# Start services using Docker Compose

up:
docker-compose up -d

# Stop services

down:
docker-compose down

# make migrations

make-migrate:
alembic revision --autogenerate -m "${CURRENT_TIMESTAMP} migration"

# Run database migrations (if using Alembic)

migrate:
alembic upgrade head

# Run tests

test:
pytest

# Format code using black and isort

format:
black .
isort .

# Run the MCP server (optional)

mcp:
uvicorn app.mcp_server:app --reload
