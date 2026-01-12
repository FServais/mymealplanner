#!/bin/bash
# Resume a paused migration
# Usage: ./migration-resume.sh

API_URL="https://meal.servais-devos.com"
PROVIDER="gemini"
RATE_LIMIT="1.0"

echo "Resuming migration..."
curl -X POST "${API_URL}/migration/resume?provider=${PROVIDER}&rate_limit=${RATE_LIMIT}" \
    -H "Content-Type: application/json" | jq .

echo ""
echo "Migration resumed. Use ./migration-status.sh to check progress."
