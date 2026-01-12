#!/bin/bash
# Watch migration progress in real-time
# Usage: ./migration-watch.sh

API_URL="https://meal.servais-devos.com"

echo "Watching migration progress (Ctrl+C to stop)..."
echo ""

while true; do
    clear
    echo "=== Migration Status ($(date)) ==="
    echo ""
    curl -s "${API_URL}/migration/status" | jq -r '
        "Running:    \(.is_running)",
        "Paused:     \(.is_paused)",
        "",
        "Total:      \(.total_recipes)",
        "Pending:    \(.pending)",
        "Processing: \(.processing)",
        "Completed:  \(.completed)",
        "Failed:     \(.failed)",
        "Skipped:    \(.skipped)",
        "",
        "Progress:   \(.completed + .failed + .skipped)/\(.total_recipes) (\(((.completed + .failed + .skipped) * 100 / .total_recipes) | floor)%)"
    '
    sleep 5
done
