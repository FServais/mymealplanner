#!/bin/bash
# Pause running migration (can be resumed later)
# Usage: ./migration-pause.sh

API_URL="https://meal.servais-devos.com"

echo "Pausing migration..."
curl -X POST "${API_URL}/migration/pause" | jq .

echo ""
echo "Migration will pause after current recipe. Use ./migration-resume.sh to continue."
