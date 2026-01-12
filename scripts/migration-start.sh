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

response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/migration/start?provider=${PROVIDER}&rate_limit=${RATE_LIMIT}&fresh=${FRESH}" \
    -H "Content-Type: application/json")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo ""
if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
    echo "$body" | jq . 2>/dev/null || echo "$body"
    echo ""
    echo "Migration started. Use ./migration-status.sh to check progress."
else
    echo "Error (HTTP $http_code):"
    echo "$body" | jq . 2>/dev/null || echo "$body"
fi
