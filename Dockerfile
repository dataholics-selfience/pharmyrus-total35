# Pharmyrus v30.3-PREDICTIVE Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements FIRST (better Docker cache)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy main application
COPY main_v30.3_PREDICTIVE.py main.py

# Copy predictive layer (v30.3 NEW)
COPY predictive_layer.py .
COPY applicant_learning.py .
COPY applicant_database.json .

# Copy existing crawlers (v30.2 - REQUIRED)
COPY google_patents_crawler.py .
COPY inpi_crawler.py .
COPY merge_logic.py .
COPY patent_cliff.py .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]