#!/bin/bash
# Gunicorn with Uvicorn workers (best for production)

echo "Starting Recipe Manager API (Gunicorn + Uvicorn Workers)"
echo "=============================================="
echo "Features:"
echo "  - 4 Uvicorn worker processes"
echo "  - High concurrency and reliability"
echo "  - NO auto-reload (restart manually after code changes)"
echo "=============================================="

# Install gunicorn if not already installed
pip install gunicorn 2>/dev/null || true

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 30 \
  --log-level info
