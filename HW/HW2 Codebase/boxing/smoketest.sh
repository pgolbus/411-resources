#!/bin/bash

echo "Running smoketests..."

BASE_URL="http://localhost:5001/api"

# Clear existing data
echo "Clearing boxers from ring..."
curl -s -X POST "$BASE_URL/clear-boxers" | jq

# Healthcheck
echo "Checking health..."
curl -s "$BASE_URL/health" | jq

# DB check
echo "Checking DB..."
curl -s "$BASE_URL/db-check" | jq

# Add first boxer
echo "Adding boxer Ali..."
curl -s -X POST "$BASE_URL/add-boxer" \
  -H "Content-Type: application/json" \
  -d '{"name": "Ali", "weight": 150, "height": 70, "reach": 72.5, "age": 25}' | jq

# Add second boxer
echo "Adding boxer Tyson..."
curl -s -X POST "$BASE_URL/add-boxer" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tyson", "weight": 160, "height": 72, "reach": 73.5, "age": 30}' | jq

# Enter both into ring
echo "Entering Ali into ring..."
curl -s -X POST "$BASE_URL/enter-ring" \
  -H "Content-Type: application/json" \
  -d '{"name": "Ali"}' | jq

echo "Entering Tyson into ring..."
curl -s -X POST "$BASE_URL/enter-ring" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tyson"}' | jq

# Trigger a fight
echo "Triggering fight..."
curl -s "$BASE_URL/fight" | jq

# Try to add third boxer to ring (should fail)
echo "Trying to add third boxer (should fail)..."
curl -s -X POST "$BASE_URL/enter-ring" \
  -H "Content-Type: application/json" \
  -d '{"name": "Ali"}' | jq

# Leaderboard check
echo "Getting leaderboard..."
curl -s "$BASE_URL/leaderboard" | jq

# Done
echo "Smoketests complete."