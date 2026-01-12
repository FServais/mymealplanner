#!/bin/bash
# Resume a paused migration
# Usage: ./migration-resume.sh

API_URL="https://meal.servais-devos.com"
PROVIDER="gemini"
RATE_LIMIT="1.0"

echo "Resuming migration..."

response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/migration/resume?provider=${PROVIDER}&rate_limit=${RATE_LIMIT}" \
    -H "Content-Type: application/json")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo ""
if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
    echo "$body" | jq . 2>/dev/null || echo "$body"
    echo ""
    echo "Migration resumed. Use ./migration-status.sh to check progress."
else
    echo "Error (HTTP $http_code):"
    echo "$body" | jq . 2>/dev/null || echo "$body"
fi
