# Pharmyrus v30.3-PREDICTIVE - Complete Integration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy main application (v30.3 integrated)
COPY main_v30.3_INTEGRATED.py main.py

# Copy v30.3 predictive layer
COPY predictive_layer.py .
COPY applicant_learning.py .
COPY applicant_database.json .

# Copy v30.2 existing modules (ALL REQUIRED)
COPY google_patents_crawler.py .
COPY inpi_crawler.py .
COPY merge_logic.py .
COPY patent_cliff.py .
COPY wipo_crawler.py .
COPY celery_app.py .
COPY family_resolver.py .
COPY materialization.py .
COPY tasks.py .
COPY wipo_crawler_v2.py .

# Copy core module (if exists, won't fail if missing)
COPY core ./core

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
