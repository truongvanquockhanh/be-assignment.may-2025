# Dockerfile for FastAPI app
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run Alembic migrations then start FastAPI app
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
