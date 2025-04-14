#!/bin/bash

# Starting Smoke Test for Boxing API
BASE_URL="http://localhost:5000"
TEST_BOXER_NAME="smoketest_boxer_$(date +%s)"
CLEANUP=true

echo "Running Healthcheck..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health")
if [ "$response" -eq 200 ]; then
  echo "✓ Healthcheck passed"
else
  echo "✗ Healthcheck failed with status code $response"
  exit 1
fi

echo "Running DB Check..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/db-check")
if [ "$response" -eq 200 ]; then
  echo "✓ DB check passed"
else
  echo "✗ DB check failed with status code $response"
  exit 1
fi

# Add Boxer Test
echo "Running Add Boxer..."
add_response=$(curl -s -X POST "$BASE_URL/api/add-boxer" \
  -d "{
    \"name\": \"$TEST_BOXER_NAME\",
    \"weight\": 125,
    \"height\": 180,
    \"reach\": 75.5,
    \"age\": 25
  }" \
  -H "Content-Type: application/json")

http_code=$(echo "$add_response" | jq -r '.status_code' 2>/dev/null || echo "")
if [ -z "$http_code" ]; then
  http_code=$(echo "$add_response" | grep -oP '"status": *"\K[^"]*' 2>/dev/null || echo "")
fi

if [[ "$add_response" == *"success"* ]] || [[ "$http_code" == "201" ]]; then
  echo "✓ Add Boxer passed"
  # Extract ID from response - adjust this based on your actual API response structure
  BOXER_ID=$(echo "$add_response" | jq -r '.id' 2>/dev/null || echo "")
  if [ -z "$BOXER_ID" ]; then
    # Alternative method to get ID if jq fails
    BOXER_ID=$(echo "$add_response" | grep -oP '"id": *\K[0-9]+' 2>/dev/null || echo "")
  fi
  echo "Created boxer ID: $BOXER_ID"
else
  echo "✗ Add Boxer failed"
  echo "Response: $add_response"
  exit 1
fi

# Get Boxer By ID Test
echo "Running Get Boxer By ID..."
if [ -z "$BOXER_ID" ]; then
  echo "⚠ No boxer ID available, skipping test"
else
  response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/get-boxer-by-id/$BOXER_ID")
  if [ "$response" -eq 200 ]; then
    echo "✓ Get Boxer By ID passed"
  else
    echo "✗ Get Boxer By ID failed with status code $response"
    echo "Tried to get boxer with ID: $BOXER_ID"
    $CLEANUP && exit 1
  fi
fi


# Get Boxer By Name Test
echo "Running Get Boxer By Name..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/get-boxer-by-name/$TEST_BOXER_NAME")
if [ "$response" -eq 200 ]; then
  echo "✓ Get Boxer By Name passed"
else
  echo "✗ Get Boxer By Name failed with status code $response"
  $CLEANUP && exit 1
fi

# Enter Ring Test
echo "Running Enter Ring..."
response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/api/enter-ring" \
  -d "{\"name\": \"$TEST_BOXER_NAME\"}" \
  -H "Content-Type: application/json" \
  -o response.json)

http_code=$(echo "$response" | tail -n 1)
if [ "$http_code" -eq 200 ]; then
  echo "✓ Enter Ring passed"
else
  echo "✗ Enter Ring failed with status code $http_code"
  cat response.json
  $CLEANUP && exit 1
fi

# Get Boxers Test
echo "Running Get Boxers..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/get-boxers")
if [ "$response" -eq 200 ]; then
  echo "✓ Get Boxers passed"
else
  echo "✗ Get Boxers failed with status code $response"
  $CLEANUP && exit 1
fi

# Bout Test (requires 2 boxers in ring)
echo "Running Bout..."
# First add another boxer for the fight
TEST_BOXER_NAME_2="${TEST_BOXER_NAME}_opponent"
curl -s -X POST "$BASE_URL/api/add-boxer" \
  -d "{
    \"name\": \"$TEST_BOXER_NAME_2\",
    \"weight\": 130,
    \"height\": 185,
    \"reach\": 76,
    \"age\": 27
  }" \
  -H "Content-Type: application/json" >/dev/null

# Enter second boxer into ring
curl -s -X POST "$BASE_URL/api/enter-ring" \
  -d "{\"name\": \"$TEST_BOXER_NAME_2\"}" \
  -H "Content-Type: application/json" >/dev/null

# Now test the fight
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/fight")
if [ "$response" -eq 200 ]; then
  echo "✓ Bout passed"
else
  echo "✗ Bout failed with status code $response"
  $CLEANUP && exit 1
fi

# Clear Boxers Test
echo "Running Clear Boxers..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/clear-boxers")
if [ "$response" -eq 200 ]; then
  echo "✓ Clear Boxers passed"
else
  echo "✗ Clear Boxers failed with status code $response"
  $CLEANUP && exit 1
fi

# Leaderboard Test
echo "Running Get Leaderboard..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/leaderboard")
if [ "$response" -eq 200 ]; then
  echo "✓ Get Leaderboard passed"
else
  echo "✗ Get Leaderboard failed with status code $response"
  $CLEANUP && exit 1
fi

# Cleanup
if [ "$CLEANUP" = true ] && [ -n "$BOXER_ID" ]; then
  echo "Cleaning up test data..."
  # Delete test boxers
  curl -s -X DELETE "$BASE_URL/api/delete-boxer/$BOXER_ID" >/dev/null
  curl -s -X POST "$BASE_URL/api/clear-boxers" >/dev/null
fi

echo "✅ Smoke tests completed"
exit 0