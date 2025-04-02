#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://127.0.0.1:5001/api"
# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  response=$(curl -s -X GET "$BASE_URL/health")
  echo "Raw response: $response"
  
  # Check if the response contains "status":"success" (no space) or "status": "success" (with space)
  if echo "$response" | grep -q '"status":"success"' || echo "$response" | grep -q '"status": "success"'; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    echo "Response doesn't contain expected success status."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  response=$(curl -s -X GET "$BASE_URL/db-check")
  echo "Raw response: $response"
  
  if echo "$response" | grep -q '"status":"success"' || echo "$response" | grep -q '"status": "success"'; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    echo "Response doesn't contain expected success status."
    exit 1
  fi
}

##########################################################
#
# Boxer Management
#
##########################################################

add_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding boxer ($name, $weight kg, $height cm, $reach inches, $age years old) to the gym..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer added successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add boxer."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

test_duplicate_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Testing duplicate boxer error (expected failure)..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")
  
  if echo "$response" | grep -q '"status": "error"'; then
    echo "Duplicate boxer test passed: Server rejected duplicate boxer as expected."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Duplicate boxer test failed: Server should have rejected duplicate boxer."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

delete_boxer_by_id() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

get_boxer_by_name() {
  boxer_name=$1

  echo "Getting boxer by name ($boxer_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$(echo $boxer_name | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (name $boxer_name):"
      if command -v jq >/dev/null 2>&1; then
        echo "$response" | jq .
      else
        echo "$response"
      fi
    fi
  else
    echo "Failed to get boxer by name ($boxer_name)."
    echo "Response:"
    if command -v jq >/dev/null 2>&1; then
      echo "$response" | jq .
    else
      echo "$response"
    fi
    exit 1
  fi
}

############################################################
#
# Ring Management
#
############################################################

enter_ring() {
  boxer_name=$1

  echo "Boxer $boxer_name entering the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\":\"$boxer_name\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer $boxer_name entered the ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Ring JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to enter boxer $boxer_name into the ring."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

test_third_boxer_in_ring() {
  boxer_name=$1

  echo "Testing third boxer in ring error (expected failure)..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\":\"$boxer_name\"}")

  if echo "$response" | grep -q '"status": "error"'; then
    echo "Third boxer test passed: Server rejected third boxer as expected."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Third boxer test failed: Server should have rejected third boxer."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

clear_ring() {
  echo "Clearing the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to clear the ring."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

fight() {
  echo "Starting fight..."
  response=$(curl -s -X GET "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    winner=$(echo "$response" | jq -r '.winner')
    echo "Fight completed successfully. Winner: $winner"
    if [ "$ECHO_JSON" = true ]; then
      echo "Fight JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to complete the fight."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

get_boxers_in_ring() {
  echo "Getting boxers in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers in the ring retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxers in the ring."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

############################################################
#
# Leaderboard
#
############################################################

get_leaderboard() {
  sort_type=$1

  echo "Getting leaderboard (sorted by $sort_type)..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_type")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    echo "Response:"
    echo "$response" | jq .
    exit 1
  fi
}

# Run the tests
check_health
check_db

# Add boxers
add_boxer "Mike Tyson" 220 180 71 35
add_boxer "Evander Holyfield" 215 189 75 32
add_boxer "Floyd Mayweather" 150 170 72 28

# Test duplicate boxer error
test_duplicate_boxer "Mike Tyson" 220 180 71 35

# Retrieve boxers
get_boxer_by_id 1
get_boxer_by_name "Mike Tyson"

# Enter ring and fight
enter_ring "Mike Tyson"
enter_ring "Evander Holyfield"

# Test third boxer in ring error
test_third_boxer_in_ring "Floyd Mayweather"

# Get boxers in ring
get_boxers_in_ring

# Start fight
fight

# Check leaderboard
get_leaderboard "wins"
get_leaderboard "win_pct"

# Clear ring
clear_ring

# Delete boxer
delete_boxer_by_id 1

echo "All tests passed successfully!"