FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps first
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENV FLASK_APP=run.py

ENTRYPOINT ["/app/entrypoint.sh"]