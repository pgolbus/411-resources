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

# Function to check the health of the service
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

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
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

  echo "Adding boxer ($name) to the ring..."
  curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer added successfully."
  else
    echo "Failed to add boxer."
    exit 1
  fi
}

delete_boxer() {
  boxer_id=$1
  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
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
    exit 1
  fi
}

get_boxer_by_name() {
  boxer_name=$1

  echo "Getting boxer by name ($boxer_name)..."
  encoded_name=$(echo "$boxer_name" | sed 's/ /%20/g')
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$encoded_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (name $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name ($boxer_name)."
    exit 1
  fi
}

###############################################
#
# Ring Management
#
###############################################


clear_ring() {
  echo "Clearing ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
  else
    echo "Failed to clear ring."
    exit 1
  fi
}

enter_ring() {
  name=$1
  echo "Entering boxer into ring: $name..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer entered ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Ring JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to enter boxer to ring."
    exit 1
  fi
}

get_boxers() {
  echo "Retrieving boxers from the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
     fi
  else
    echo "Failed to retrieve boxers."
    exit 1
  fi
}

fight() {
  echo "Starting a fight between boxers..."
  response=$(curl -s -X GET "$BASE_URL/fight")
  if echo "$response" | grep -q '"status": "success"'; then
    winner=$(echo "$response" | jq -r '.winner')
    echo "Fight completed successfully. Winner: $winner"
    if [ "$ECHO_JSON" = true ]; then
      echo "Fight Result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to start a fight."
    exit 1
  fi
}


############################################################
#
# Leaderboard
#
############################################################

get_boxer_leaderboard() {
  echo "Getting boxer leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by wins):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer leaderboard."
    exit 1
  fi
}


# Health Checks
check_health
check_db

# Add boxers
add_boxer "Boxer 1" 150 68 70 30
add_boxer "Boxer 2" 155 70 72 28

get_boxer_by_id 1
get_boxer_by_id 2

get_boxer_by_name "Boxer 1"
get_boxer_by_name "Boxer 2"

add_boxer "Boxer 3" 160 66 68 32
delete_boxer 3

clear_ring

enter_ring "Boxer 1"
enter_ring "Boxer 2"
get_boxers
fight
get_boxers

enter_ring "Boxer 1"
clear_ring
get_boxers

get_boxer_leaderboard

echo "All tests passed  successfully!"

