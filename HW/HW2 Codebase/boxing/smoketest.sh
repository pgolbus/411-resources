#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

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
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##############################################
#
# Gym
#
##############################################

create_boxer() {
  echo "Adding a boxer..."
  curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d '{"name":"Muhammad Ali", "weight":210, "height":191, "reach":78, "age":32}' | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer added successfully."
  else
    echo "Failed to add boxer."
    exit 1
  fi
}

delete_boxer_by_id() {
  echo "Deleting boxer by ID (1)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/1")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID (1)."
  else
    echo "Failed to delete boxer by ID (1)."
    exit 1
  fi
}

get_boxer_by_id() {
  echo "Getting boxer by ID (1)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/1")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID (1)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (ID 1):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID (1)."
    exit 1
  fi
}

get_boxer_by_name() {
  echo "Getting boxer by name (Muhammad Ali)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/Muhammad%20Ali")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name (Muhammad Ali)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Muhammad Ali):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name (Muhammad Ali)."
    exit 1
  fi
}

############################################
#
# Bout
#
############################################

clear_boxers() {
  echo "Clearing boxers from the ring..."
  curl -s -X POST "$BASE_URL/clear-boxers" -H "Content-Type: application/json" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxers cleared successfully."
  else
    echo "Failed to clear boxers."
    exit 1
  fi
}

get_boxers() {
  echo "Getting the current list of boxers in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  # Check if the response contains boxers or an empty list
  if echo "$response" | grep -q '"boxers"'; then
    echo "Boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxers or no boxers found."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error or empty response:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

enter_ring() {
  echo "Entering a boxer into the ring..."
  curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d '{"name":"Muhammad Ali"}' | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxer entered the ring successfully."
  else
    echo "Failed to enter boxer into the ring."
    exit 1
  fi
}

run_bout() {
  echo "Running a bout..."
  curl -s -X GET "$BASE_URL/bout" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Bout completed successfully."
  else
    echo "Failed to complete bout."
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

get_leaderboard_wins() {
  echo "Getting leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard by wins retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by wins):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard by wins."
    exit 1
  fi
}

get_leaderboard_win_pct() {
  echo "Getting leaderboard sorted by win percentage..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=win_pct")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard by win percentage retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by win percentage):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard by win percentage."
    exit 1
  fi
}


# Initialize the database
sqlite3 db/boxing.db < sql/init_db.sql

# Run all the steps in order
check_health
check_db
create_boxer
clear_boxers
enter_ring
enter_ring
get_boxers
get_leaderboard_wins
get_leaderboard_win_pct
get_boxer_by_name
get_boxer_by_id
delete_boxer_by_id


echo "All tests passed successfully!"
