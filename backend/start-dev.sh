#!/bin/bash
# Development server startup script with optimized concurrency settings

echo "Starting Recipe Manager API (Development Mode)"
echo "=============================================="
echo "Features:"
echo "  - Auto-reload enabled"
echo "  - Increased connection limits"
echo "  - Optimized for concurrent requests"
echo "=============================================="

uvicorn main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --limit-concurrency 50 \
  --backlog 500 \
  --timeout-keep-alive 30 \
  --log-level info
