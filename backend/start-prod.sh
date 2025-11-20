#!/bin/bash
# Production-style server with multiple workers (no auto-reload)

echo "Starting Recipe Manager API (Multi-Worker Mode)"
echo "=============================================="
echo "Features:"
echo "  - 4 worker processes"
echo "  - High concurrency"
echo "  - NO auto-reload (restart manually after code changes)"
echo "=============================================="

uvicorn main:app \
  --host 0.0.0.0 \
  --port 8082 \
  --workers 4 \
  --limit-concurrency 100 \
  --backlog 500 \
  --timeout-keep-alive 30 \
  --log-level info
