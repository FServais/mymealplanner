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
    curl -s "${API_URL}/migration/results?status=${STATUS}&limit=50" | jq .
else
    echo "Fetching all migration results..."
    curl -s "${API_URL}/migration/results?limit=50" | jq .
fi
