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

create_boxer() {
  name=$1
  weight=$3
  height=$4
  reach=$5
  age=$6

  echo "Adding boxer ($name, $weight, $height, $reach, $age)..."
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

get_leaderboard() {
  sort_by=$1

  echo "Getting leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort_by=$sort_by")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard sorted by $sort_by:"
    echo "$response" | jq '.leaderboard'
    if [ "$ECHO_JSON" = true ]; then
      echo "Full response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard sorted by $sort_by."
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
  name=$1

  echo "Getting boxer by name ($name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$boxer_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name ($name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name ($name)."
    exit 1
  fi
}

get_weight_class() {
  weight=$1

  echo "Getting weight class for weight ($weight)..."
  response=$(curl -s -X GET "$BASE_URL/get-weight-class?weight=$weight")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weight class for weight $weight: $(echo "$response" | jq .weight_class)"
    if [ "$ECHO_JSON" = true ]; then
      echo "Full response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get weight class for weight $weight."
    exit 1
  fi
}

update_boxer_stats() {
  boxer_id=$1
  result=$2

  echo "Updating stats for boxer ID ($boxer_id) with result ($result)..."
  response=$(curl -s -X POST "$BASE_URL/update-boxer-stats" -H "Content-Type: application/json" \
    -d "{\"boxer_id\":$boxer_id, \"result\":\"$result\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stats updated for boxer ID $boxer_id with result $result."
    if [ "$ECHO_JSON" = true ]; then
      echo "Full response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to update stats for boxer ID $boxer_id."
    exit 1
  fi
}

############################################################
#
# Ring Management
#
############################################################

enter_ring() {
  boxer_id=$1

  echo "Adding boxer with ID $boxer_id to the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"boxer_id\":$boxer_id}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer with ID $boxer_id added to the ring."
    if [ "$ECHO_JSON" = true ]; then
      echo "Full response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add boxer with ID $boxer_id to the ring."
    exit 1
  fi
}

fight() {
  echo "Simulating fight between two boxers..."
  response=$(curl -s -X POST "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    winner=$(echo "$response" | jq -r '.winner')
    echo "Fight result: $winner wins."
    if [ "$ECHO_JSON" = true ]; then
      echo "Full response:"
      echo "$response" | jq .
    fi
  else
    echo "Fight failed."
    exit 1
  fi
}

clear_ring() {
  echo "Clearing the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared."
    if [ "$ECHO_JSON" = true ]; then
      echo "Full response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to clear the ring."
    exit 1
  fi
}

get_boxers() {
  echo "Getting boxers currently in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers in the ring:"
    if [ "$ECHO_JSON" = true ]; then
      echo "Full response:"
      echo "$response" | jq .
    else
      echo "$response" | jq -r '.boxers[] | .name'
    fi
  else
    echo "Failed to retrieve boxers."
    exit 1
  fi
}

get_fighting_skill() {
  boxer_id=$1

  echo "Getting fighting skill for boxer with ID $boxer_id..."
  response=$(curl -s -X GET "$BASE_URL/get-fighting-skill/$boxer_id")

  if echo "$response" | grep -q '"status": "success"'; then
    skill=$(echo "$response" | jq -r '.fighting_skill')
    echo "Fighting skill for boxer with ID $boxer_id: $skill"
    if [ "$ECHO_JSON" = true ]; then
      echo "Full response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve fighting skill for boxer with ID $boxer_id."
    exit 1
  fi
}

# Initialize the database
sqlite3 db/ring.db < sql/init_db.sql

# Health checks
check_health
check_db

create_boxer "Mike Tyson" "Heavyweight" 250 75 80 60
create_boxer "Muhammad Ali" "Heavyweight" 200 75 80 40
create_boxer "Canelo Alvarez" "Welterweight" 185 69 69 69

delete_boxer 1

get_boxer_by_id 2
get_boxer_by_name "Muhammad Ali"
get_weight_class 200

update_boxer_stats 2 "win"

enter_ring 2
enter_ring 3

get_boxers

fight

clear_ring

get_boxers

get_fighting_skill 2

get_leaderboard "wins"

echo "All tests passed successfully!"