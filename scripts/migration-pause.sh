#!/bin/bash
# Pause running migration (can be resumed later)
# Usage: ./migration-pause.sh

API_URL="https://meal.servais-devos.com"

echo "Pausing migration..."

response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/migration/pause")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo ""
if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
    echo "$body" | jq . 2>/dev/null || echo "$body"
    echo ""
    echo "Use ./migration-resume.sh to continue."
else
    echo "Error (HTTP $http_code):"
    echo "$body" | jq . 2>/dev/null || echo "$body"
fi
