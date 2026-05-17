# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (for XGBoost and Prisma)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the API service
COPY services/api/requirements.txt .
# Add core requirements as well
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r services/api/requirements.txt

# Copy the core engine and models
COPY core /app/core

# Copy the API service code
COPY services/api /app/services/api

# Set environment variables
ENV PYTHONPATH="/app"
ENV DATABASE_URL="postgresql://postgres:postgres@db:5432/complyance"

# Initialize Prisma
WORKDIR /app/services/api
RUN prisma generate --schema=prisma/schema.prisma

# Expose the port the app runs on
EXPOSE 3001

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]
