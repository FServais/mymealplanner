#!/bin/bash
# Reset migration progress (clear all records)
# Usage: ./migration-reset.sh

API_URL="https://meal.servais-devos.com"

echo "WARNING: This will clear all migration progress!"
read -p "Are you sure? (y/N): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "Resetting migration..."

    response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/migration/reset")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo ""
    if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        echo "Error (HTTP $http_code):"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    fi
else
    echo "Cancelled."
fi
