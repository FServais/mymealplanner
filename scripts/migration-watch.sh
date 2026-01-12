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

    response=$(curl -s -w "\n%{http_code}" "${API_URL}/migration/status")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
        echo "$body" | jq -r '
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
            "Progress:   \(.completed + .failed + .skipped)/\(.total_recipes) (\(if .total_recipes > 0 then ((.completed + .failed + .skipped) * 100 / .total_recipes | floor) else 0 end)%)"
        ' 2>/dev/null || echo "$body"
    else
        echo "Error (HTTP $http_code):"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    fi

    sleep 5
done
