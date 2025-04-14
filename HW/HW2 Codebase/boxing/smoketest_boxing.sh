#!/bin/bash

# Starting Smoke Test for Boxing API
BASE_URL="http://localhost:5001"
TEST_BOXER_NAME="smoketest_boxer_$(date +%s)"
CLEANUP=true

echo "Running Healthcheck..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health")
if [ "$response" -eq 200 ]; then
  echo "[PASS] Healthcheck passed"
else
  echo "[FAIL] Healthcheck failed with status code $response"
  exit 1
fi

echo "Running DB Check..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/db-check")
if [ "$response" -eq 200 ]; then
  echo "[PASS] DB check passed"
else
  echo "[FAIL] DB check failed with status code $response"
  exit 1
fi

# Add Boxer
echo "Adding test boxer..."
add_response=$(curl -s -X POST "$BASE_URL/api/add-boxer" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$TEST_BOXER_NAME\", \"weight\": 125, \"height\": 180, \"reach\": 75.5, \"age\": 25}")

if echo "$add_response" | grep -q '"status": "success"'; then
  echo "[PASS] Add Boxer passed"
else
  echo "[FAIL] Add Boxer failed"
  echo "$add_response"
  exit 1
fi

# Get Boxer By Name
echo "Getting boxer by name..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/get-boxer-by-name/$TEST_BOXER_NAME")
if [ "$response" -eq 200 ]; then
  echo "[PASS] Get Boxer by Name passed"
else
  echo "[FAIL] Get Boxer by Name failed with status $response"
  exit 1
fi

# Enter Ring
echo "Entering boxer into ring..."
response=$(curl -s -X POST "$BASE_URL/api/enter-ring" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$TEST_BOXER_NAME\"}")
if echo "$response" | grep -q '"status": "success"'; then
  echo "[PASS] Enter Ring passed"
else
  echo "[FAIL] Enter Ring failed"
  echo "$response"
  exit 1
fi

# Add second boxer
TEST_BOXER_NAME_2="${TEST_BOXER_NAME}_opponent"
echo "Adding second boxer..."
curl -s -X POST "$BASE_URL/api/add-boxer" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$TEST_BOXER_NAME_2\", \"weight\": 130, \"height\": 185, \"reach\": 76, \"age\": 27}" >/dev/null

# Enter second boxer
curl -s -X POST "$BASE_URL/api/enter-ring" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$TEST_BOXER_NAME_2\"}" >/dev/null

# Trigger Bout
echo "Triggering bout..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/fight")
if [ "$response" -eq 200 ]; then
  echo "[PASS] Bout passed"
else
  echo "[FAIL] Bout failed with status $response"
  exit 1
fi

# Get Boxers
echo "Getting boxers in ring..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/get-boxers")
if [ "$response" -eq 200 ]; then
  echo "[PASS] Get Boxers passed"
else
  echo "[FAIL] Get Boxers failed with status $response"
  exit 1
fi

# Clear Boxers
echo "Clearing boxers..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/clear-boxers")
if [ "$response" -eq 200 ]; then
  echo "[PASS] Clear Boxers passed"
else
  echo "[FAIL] Clear Boxers failed with status $response"
  exit 1
fi

# Leaderboard
echo "Getting leaderboard..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/leaderboard")
if [ "$response" -eq 200 ]; then
  echo "[PASS] Get Leaderboard passed"
else
  echo "[FAIL] Get Leaderboard failed with status $response"
  exit 1
fi

# Final Cleanup (optional)
echo "Final cleanup..."
curl -s -X POST "$BASE_URL/api/clear-boxers" >/dev/null

echo "Smoke tests completed successfully."
exit 0
