# Pharmyrus v30.3-PREDICTIVE - Complete Integration
# Using bullseye (Debian 11) instead of trixie to avoid font package issues
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies including Playwright requirements
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
# Using system dependencies approach instead of playwright install-deps
RUN playwright install chromium && \
    apt-get update && \
    apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Copy main application (v30.3 integrated)
COPY main_v30.3_INTEGRATED.py main.py

# Copy v30.3 predictive layer
COPY predictive_layer.py .
COPY applicant_learning.py .
COPY applicant_database.json .

# Copy v30.2 existing modules
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

# Copy core module
COPY core ./core

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
