#!/bin/bash
# Start ingredient migration (fresh start or continue from where left off)
# Usage: ./migration-start.sh [--fresh]

API_URL="https://meal.servais-devos.com"
PROVIDER="gemini"
RATE_LIMIT="1.0"

FRESH="false"
if [[ "$1" == "--fresh" ]]; then
    FRESH="true"
    echo "Starting FRESH migration (clearing previous progress)..."
else
    echo "Starting migration (continuing from previous progress)..."
fi

curl -X POST "${API_URL}/migration/start?provider=${PROVIDER}&rate_limit=${RATE_LIMIT}&fresh=${FRESH}" \
    -H "Content-Type: application/json" | jq .

echo ""
echo "Migration started. Use ./migration-status.sh to check progress."
