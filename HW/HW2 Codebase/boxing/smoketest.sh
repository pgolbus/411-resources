#!/bin/bash

BASE_URL="http://localhost:5001/api"
ECHO_JSON=false

# Optional: Echo JSON output with --echo-json
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

###############################################
# Health Checks
###############################################
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Service is healthy." || { echo "Health check failed."; exit 1; }
}

check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Database is healthy." || { echo "Database check failed."; exit 1; }
}

###############################################
# Boxer Management
###############################################
add_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding boxer: $name"
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\", \"weight\": $weight, \"height\": $height, \"reach\": $reach, \"age\": $age}")

  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Boxer added successfully." || { echo "Failed to add boxer."; echo "$response"; exit 1; }
}

delete_boxer_by_id() {
  id=$1
  echo "Deleting boxer with ID: $id"
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$id")
  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Boxer deleted successfully." || { echo "Failed to delete boxer."; echo "$response"; exit 1; }
}

get_boxer_by_id() {
  id=$1
  echo "Getting boxer by ID: $id"
  response=$(curl -s "$BASE_URL/get-boxer-by-id/$id")
  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Boxer retrieved successfully." || { echo "Failed to retrieve boxer."; echo "$response"; exit 1; }
  $ECHO_JSON && echo "$response" | jq .
}

get_boxer_by_name() {
  name=$1
  echo "Getting boxer by name: $name"
  response=$(curl -s "$BASE_URL/get-boxer-by-name/$name")
  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Boxer retrieved successfully." || { echo "Failed to retrieve boxer."; echo "$response"; exit 1; }
  $ECHO_JSON && echo "$response" | jq .
}

###############################################
# Ring Management
###############################################
enter_ring() {
  name=$1
  echo "Adding $name to the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d "{\"name\": \"$name\"}")
  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "$name entered the ring successfully." || { echo "Failed to enter ring."; echo "$response"; exit 1; }
}

clear_boxers() {
  echo "Clearing all boxers from the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Ring cleared successfully." || { echo "Failed to clear ring."; echo "$response"; exit 1; }
}

get_boxers_in_ring() {
  echo "Getting all boxers in the ring..."
  response=$(curl -s "$BASE_URL/get-boxers")
  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Retrieved boxers in ring." || { echo "Failed to get boxers."; echo "$response"; exit 1; }
  $ECHO_JSON && echo "$response" | jq .
}

fight() {
  echo "Triggering a fight..."
  response=$(curl -s "$BASE_URL/fight")
  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Fight complete." || { echo "Fight failed."; echo "$response"; exit 1; }
  $ECHO_JSON && echo "$response" | jq .
}

###############################################
# Leaderboard
###############################################
get_leaderboard() {
  sort=$1
  echo "Getting leaderboard sorted by $sort..."
  response=$(curl -s "$BASE_URL/leaderboard?sort=$sort")
  echo "$response" | grep -q '"status": "success"'
  [[ $? -eq 0 ]] && echo "Leaderboard retrieved successfully." || { echo "Failed to retrieve leaderboard."; echo "$response"; exit 1; }
  $ECHO_JSON && echo "$response" | jq .
}

###############################################
# Run Sequence
###############################################
check_health
check_db

add_boxer "Ilia Topuria" 145 67 69.0 28
add_boxer "Jon Jones" 250 76 84.5 36

get_boxer_by_name "Ilia Topuria"
get_boxer_by_id 1

enter_ring "Ilia Topuria"
enter_ring "Jon Jones"
get_boxers_in_ring
fight

get_leaderboard "wins"
get_leaderboard "win_pct"

clear_boxers
delete_boxer_by_id 1

echo "All tests passed successfully!"
