#!/bin/bash
# Check migration status
# Usage: ./migration-status.sh

API_URL="https://meal.servais-devos.com"

response=$(curl -s -w "\n%{http_code}" "${API_URL}/migration/status")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    echo "Error (HTTP $http_code):"
    echo "$body" | jq . 2>/dev/null || echo "$body"
fi
