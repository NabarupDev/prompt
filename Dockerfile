# Dockerfile for Prompt Injection Detection API
# This Dockerfile builds the project from scratch, including model training.

FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all project files
COPY . .

# Set environment variables (can be overridden by .env)
ENV HOST=0.0.0.0
ENV PORT=3000
ENV LOG_LEVEL=info
ENV MODEL_PATH=./models/prompt_injection_model
ENV MAX_TEXT_LENGTH=256
ENV BATCH_SIZE_LIMIT=100
ENV REQUEST_TIMEOUT=30
ENV RELOAD=false
ENV DEBUG=false

# Train the model from scratch (will overwrite any existing model)
RUN python scripts/prepare_data.py --input-file data/original_dataset.json --balance-method undersample && \
    python scripts/train_model.py

# Expose API port
EXPOSE 3000

# Start the API server
CMD ["python", "scripts/start_server.py"]
