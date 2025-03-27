#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://127.0.0.1:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=true

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
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Creating boxer ($name, $weight, $height, $reach, $age)..."
  curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":\"$weight\", \"height\":$height, \"reach\":\"$reach\", \"age\":$age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer created successfully."
  else
    echo "Failed to create boxer."
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
  response=$(curl -s -X GET "$BASE_URL/get_boxer_by_id/$boxer_id")
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
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$(echo $boxer_name | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name."
    exit 1
  fi
}

get_leaderboard() {
  sort=$1

  echo "Getting leaderboard sorted by $sort..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    exit 1
  fi
}


############################################################
#
# Ring Management
#
############################################################

# TODO: Add Ring Smoketests


############################################################
#
# Run Tests
#
############################################################

# Initialize the database
sqlite3 db/playlist.db < sql/init_db.sql

# Health checks
check_health
check_db

# Run Smoketests
create_boxer "John Doe" 160 66 24 21
create_boxer "Jane Doe" 150 63 22 20
create_boxer "Judy Doe" 140 60 20 19

delete_boxer 2

get_boxer_by_id 0
get_boxer_by_id 1

get_boxer_by_name "John Doe"
get_boxer_by_name "Jane Doe"

get_leaderboard "wins"
get_leaderboard "win_pct"

# TODO: Run Ring Smoketests

echo "All tests passed successfully!"