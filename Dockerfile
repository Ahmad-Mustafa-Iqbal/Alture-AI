# ==============================================================================
# Alture AI — Multi-Modal NLP Intelligence & Explainable ATS Platform
# Production Multi-Stage Dockerfile
# ==============================================================================

FROM python:3.11-slim

# Set environment flags for deterministic Python execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install OS-level dependencies for C-extensions and compilers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy small English ontology parser
RUN python -m spacy download en_core_web_sm

# Copy full application codebase and pre-trained models
COPY . .

# Expose production port
EXPOSE 8000

# Healthcheck to verify operational readiness
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Production entrypoint running Uvicorn ASGI server
CMD ["sh", "-c", "uvicorn deployment.backend.main:app --host 0.0.0.0 --port ${PORT}"]
