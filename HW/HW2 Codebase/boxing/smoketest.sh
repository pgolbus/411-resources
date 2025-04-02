#!/bin/bash

BASE_URL="http://localhost:5000/api"
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unrecognized argument: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health and Database Checks
#
###############################################

check_health() {
  echo "Checking server health status..."
  curl -s "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Health check passed successfully."
  else
    echo "Health check failed. Exiting..."
    exit 1
  fi
}

check_db() {
  echo "Verifying database connection..."
  curl -s "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection verified."
  else
    echo "Database connection check failed. Exiting..."
    exit 1
  fi
}

###############################################
#
# Boxer Management Endpoints
#
###############################################

add_boxer() {
  echo "Attempting to add boxer 'David'..."
  curl -s -X POST "$BASE_URL/add-boxer" \
    -H "Content-Type: application/json" \
    -d '{"name": "David", "weight": 150, "height": 175, "reach": 70.0, "age": 30}' | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer 'David' added successfully."
  else
    echo "Failed to add boxer 'David'. Exiting..."
    exit 1
  fi
}

add_boxer2() {
  echo "Attempting to add boxer 'Goliath'..."
  curl -s -X POST "$BASE_URL/add-boxer" \
    -H "Content-Type: application/json" \
    -d '{"name": "Goliath", "weight": 250, "height": 200, "reach": 80.0, "age": 35}' | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer 'Goliath' added successfully."
  else
    echo "Failed to add boxer 'Goliath'. Exiting..."
    exit 1
  fi
}

get_boxer_by_id() {
  echo "Fetching boxer with ID 1..."
  curl -s "$BASE_URL/get-boxer-by-id/1" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer retrieved successfully by ID."
  else
    echo "Failed to retrieve boxer by ID. Exiting..."
    exit 1
  fi
}

delete_boxer() {
  echo "Deleting boxer with ID 1..."
  curl -s -X DELETE "$BASE_URL/delete-boxer/1" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer deleted successfully."
  else
    echo "Failed to delete boxer. Exiting..."
    exit 1
  fi
}

###############################################
#
# Ring and Fight Endpoints
#
###############################################

enter_ring() {
  echo "Entering boxer 'David' into the ring..."
  curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d '{"name": "David"}' | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer 'David' successfully entered the ring."
  else
    echo "Failed to enter boxer 'David' into the ring. Exiting..."
    exit 1
  fi
}

enter_ring2() {
  echo "Entering boxer 'Goliath' into the ring..."
  curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d '{"name": "Goliath"}' | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer 'Goliath' successfully entered the ring."
  else
    echo "Failed to enter boxer 'Goliath' into the ring. Exiting..."
    exit 1
  fi
}

get_boxers() {
  echo "Retrieving list of boxers in the ring..."
  curl -s "$BASE_URL/get-boxers" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Successfully retrieved list of boxers."
  else
    echo "Failed to retrieve boxers. Exiting..."
    exit 1
  fi
}

fight() {
  echo "Starting the fight between the boxers..."
  curl -s "$BASE_URL/fight" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Fight completed successfully."
  else
    echo "Fight failed. Exiting..."
    exit 1
  fi
}

clear_boxers() {
  echo "Clearing boxers from the ring..."
  curl -s -X POST "$BASE_URL/clear-boxers" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Ring cleared successfully."
  else
    echo "Failed to clear the ring. Exiting..."
    exit 1
  fi
}

get_leaderboard() {
  echo "Retrieving the leaderboard..."
  curl -s "$BASE_URL/leaderboard?sort=wins" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Leaderboard retrieved successfully."
  else
    echo "Failed to retrieve leaderboard. Exiting..."
    exit 1
  fi
}

###############################################
#
# Execute Smoketests
#
###############################################

check_health
check_db

# Add and confirm first boxer.
add_boxer
get_boxer_by_id

# Add second boxer.
add_boxer2

# Enter both boxers into the ring.
enter_ring
enter_ring2

# Retrieve boxers in the ring.
get_boxers

# Initiate fight; now that there are two boxers, this should succeed.
fight

# Retrieve leaderboard and clear the ring.
get_leaderboard
clear_boxers

# Optional: Delete boxer (if you wish to test boxer deletion separately)
delete_boxer

echo "All smoketests completed successfully!"
