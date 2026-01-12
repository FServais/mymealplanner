#!/bin/bash
# Reset migration progress (clear all records)
# Usage: ./migration-reset.sh

API_URL="https://meal.servais-devos.com"

echo "WARNING: This will clear all migration progress!"
read -p "Are you sure? (y/N): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "Resetting migration..."
    curl -X POST "${API_URL}/migration/reset" | jq .
else
    echo "Cancelled."
fi
