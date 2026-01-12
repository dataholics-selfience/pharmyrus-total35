FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

# ============================================================================
# DEPENDENCIES
# ============================================================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# CORE APPLICATION (v30.2 - STABLE)
# ============================================================================
# Main API with all crawlers integrated
COPY main_v30.3_MINIMAL.py main.py

# ============================================================================
# CRAWLERS (v30.2 - UNCHANGED)
# ============================================================================
COPY google_patents_crawler.py .   # Google Patents crawler with Playwright
COPY inpi_crawler.py .              # INPI Brasil crawler
COPY wipo_crawler.py .              # WIPO PatentScope crawler

# ============================================================================
# CORE UTILITIES (v30.2 - UNCHANGED)
# ============================================================================
COPY family_resolver.py .           # Patent family resolution
COPY materialization.py .           # Data materialization
COPY merge_logic.py .               # Patent merge logic
COPY patent_cliff.py .              # Patent cliff calculation

# ============================================================================
# CELERY ASYNC PROCESSING (v30.2 - UNCHANGED)
# ============================================================================
COPY celery_app.py .                # Celery configuration
COPY tasks.py .                     # Celery tasks

# ============================================================================
# CORE SEARCH ENGINE (v30.2 - UNCHANGED)
# ============================================================================
COPY core ./core                    # Search engine core modules

# ============================================================================
# PREDICTIVE LAYER (v30.3 - STABLE)
# ============================================================================
COPY predictive_layer.py .          # Predictive intelligence engine
COPY applicant_learning.py .        # Applicant behavior learning
COPY applicant_database.json .      # 34+ pharma companies database

# ============================================================================
# ENHANCED REPORTING (v30.4 - NEW)
# ============================================================================
COPY enhanced_reporting.py .        # Legal disclaimers & enhanced reporting
                                    # - Legal framework (PT/EN)
                                    # - Tier-based counting
                                    # - Enhanced Cortellis audit
                                    # - Future patent cliff

# ============================================================================
# CONFIGURATION
# ============================================================================
# Railway uses PORT env variable
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# ============================================================================
# STARTUP
# ============================================================================
# Run FastAPI + Celery Worker in same container
# Railway sets PORT automatically
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} & celery -A celery_app worker --loglevel=info --concurrency=1 -I tasks"
