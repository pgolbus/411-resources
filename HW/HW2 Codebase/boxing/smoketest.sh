#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

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
# Health Checks
#
###############################################

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking database connection and boxers table..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database and boxers table are healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

###############################################
#
# Boxer Management
#
###############################################

add_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding boxer ($name)..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer '$name' added successfully."
  else
    echo "Failed to add boxer '$name'."
    echo "$response"
    exit 1
  fi
}

get_boxer_by_name() {
  boxer_name=$1
  # URL-encode spaces
  encoded_boxer_name=$(echo "$boxer_name" | sed 's/ /%20/g')

  echo "Retrieving boxer by name ($boxer_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$encoded_boxer_name")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer '$boxer_name' retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve boxer '$boxer_name'."
    echo "$response"
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Retrieving boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer with ID $boxer_id retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve boxer with ID $boxer_id."
    echo "$response"
    exit 1
  fi
}

delete_boxer() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer with ID $boxer_id deleted successfully."
  else
    echo "Failed to delete boxer with ID $boxer_id."
    echo "$response"
    exit 1
  fi
}

###############################################
#
# Ring Management
#
###############################################

enter_ring() {
  boxer_name=$1

  echo "Entering boxer '$boxer_name' into the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\":\"$boxer_name\"}")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer '$boxer_name' entered the ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Ring JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to enter boxer '$boxer_name' into the ring."
    echo "$response"
    exit 1
  fi
}

get_boxers_in_ring() {
  echo "Retrieving boxers in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxers in the ring retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve boxers in the ring."
    echo "$response"
    exit 1
  fi
}

fight() {
  echo "Triggering a fight..."
  response=$(curl -s -X GET "$BASE_URL/fight")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Fight executed successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Fight result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Fight endpoint failed."
    echo "$response"
    exit 1
  fi
}

clear_boxers() {
  echo "Clearing boxers from the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxers cleared from the ring successfully."
  else
    echo "Failed to clear boxers from the ring."
    echo "$response"
    exit 1
  fi
}

###############################################
#
# Leaderboard
#
###############################################

get_leaderboard() {
  sort_field=$1
  echo "Retrieving leaderboard sorted by $sort_field..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_field")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    echo "$response"
    exit 1
  fi
}

###############################################
#
# Test Execution
#
###############################################

# Health Checks
check_health
check_db

###############################################
#
# Boxer Operations
#
###############################################

# Add a boxer
add_boxer "Mike Tyson" 126 178 71.5 35
# Retrieve boxer by name
get_boxer_by_name "Mike Tyson"

# Optional: Capture boxer id from the response using jq.
# (Assumes that the JSON response from get_boxer-by-name includes an "id" field.)
boxer_id=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/Mike%20Tyson" | jq '.boxer.id')
echo "Captured boxer ID: $boxer_id"
# Retrieve boxer by ID
get_boxer_by_id "$boxer_id"

# Delete the boxer from the database
delete_boxer "$boxer_id"

###############################################
#
# Ring Operations
#
###############################################

# Add two boxers and enter them into the ring for a fight
add_boxer "Muhammad Ali" 177 196 80 30
add_boxer "Joe Frazier" 156 183 75 32

enter_ring "Muhammad Ali"
enter_ring "Joe Frazier"
get_boxers_in_ring

# Trigger a fight between the boxers in the ring
fight

# Clear the ring
clear_boxers
get_boxers_in_ring

###############################################
#
# Leaderboard
#
###############################################

# Retrieve the leaderboard sorted by wins
get_leaderboard "wins"

echo "All tests passed successfully!"
