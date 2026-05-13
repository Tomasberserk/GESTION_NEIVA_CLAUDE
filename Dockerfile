FROM python:3.11-slim

WORKDIR /app

# Install system deps needed by psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Layer-cache: copy requirements before source
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

# Render injects PORT at runtime; default to 8000 for local docker run
ENV PORT=8000

# Shell form so $PORT is expanded at runtime
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
