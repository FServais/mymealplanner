#!/bin/bash
# View migration results
# Usage: ./migration-results.sh [status]
# Examples:
#   ./migration-results.sh           # Show all results
#   ./migration-results.sh completed # Show only completed
#   ./migration-results.sh failed    # Show only failed
#   ./migration-results.sh skipped   # Show only skipped

API_URL="https://meal.servais-devos.com"
STATUS="$1"

if [[ -n "$STATUS" ]]; then
    echo "Fetching migration results (status: $STATUS)..."
    url="${API_URL}/migration/results?status=${STATUS}&limit=50"
else
    echo "Fetching all migration results..."
    url="${API_URL}/migration/results?limit=50"
fi

response=$(curl -s -w "\n%{http_code}" "$url")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo ""
if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    echo "Error (HTTP $http_code):"
    echo "$body" | jq . 2>/dev/null || echo "$body"
fi
