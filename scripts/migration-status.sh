#!/bin/bash
# Check migration status
# Usage: ./migration-status.sh

API_URL="https://meal.servais-devos.com"

curl -s "${API_URL}/migration/status" | jq .
