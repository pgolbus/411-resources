#!/bin/bash

BASE_URL="http://localhost:5001/api"

echo "Checking health endpoint..."
curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"' && echo "Health check passed" || { echo "Health check failed"; exit 1; }

echo "Checking DB connection..."
curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"' && echo "DB check passed" || { echo "DB check failed"; exit 1; }

echo "Clearing boxers..."
curl -s -X POST "$BASE_URL/clear-boxers" > /dev/null

echo "Adding boxer Aarnav..."
curl -s -X POST "$BASE_URL/add-boxer" \
    -H "Content-Type: application/json" \
    -d '{"name": "Aarnav", "weight": 160, "height": 185, "reach": 78.5, "age": 21}' \
    | grep -q '"status": "success"' && echo "Boxer Aarnav added" || { echo "Failed to add Aarnav"; exit 1; }

echo "Adding boxer Taha..."
curl -s -X POST "$BASE_URL/add-boxer" \
    -H "Content-Type: application/json" \
    -d '{"name": "Taha", "weight": 155, "height": 180, "reach": 76.0, "age": 20}' \
    | grep -q '"status": "success"' && echo "Boxer Taha added" || { echo "Failed to add Taha"; exit 1; }

echo "Entering Aarnav into the ring..."
curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d '{"name": "Aarnav"}' | grep -q '"status": "success"' && echo "Aarnav entered ring" || exit 1

echo "Entering Taha into the ring..."
curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d '{"name": "Taha"}' | grep -q '"status": "success"' && echo "Taha entered ring" || exit 1

echo "Triggering fight..."
curl -s -X GET "$BASE_URL/fight" | grep -q '"status": "success"' && echo "Fight complete" || { echo "Fight failed"; exit 1; }

echo "Getting leaderboard..."
curl -s -X GET "$BASE_URL/leaderboard" | grep -q '"status": "success"' && echo "Leaderboard loaded" || exit 1

echo "Cleaning up boxers..."
curl -s -X POST "$BASE_URL/clear-boxers" > /dev/null

echo "Smoke tests passed!"
