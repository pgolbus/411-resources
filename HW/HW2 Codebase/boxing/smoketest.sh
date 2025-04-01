#!/bin/bash

# Define the base URL for the Flask API
PORT=5001
BASE_URL="http://localhost:$PORT/api"

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


############################################################
#
# Ring Management
#
############################################################

add_boxer_to_ring() {
  id=$1
  name=$2
  age=$3
  weight=$4
  reach=$5
  height=$6

  echo "Adding boxer: $name (ID: $id, Age: $age, Weight: $weight, Reach: $reach, Height: $height)..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"id\": $id, \"name\": \"$name\", \"age\": $age, \"weight\": $weight, \"reach\": $reach, \"height\": $height}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer added successfully."
  else
    echo "Failed to add boxer to ring."
    echo "$response"
    exit 1
  fi
}

get_all_boxers_from_ring() {
  echo "Retrieving all boxers from the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all boxers from ring."
    exit 1
  fi
}

clear_ring() {
  echo "Clearing the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-ring")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
  else
    echo "Failed to clear ring."
    exit 1
  fi
}

s

# Health checks
check_health
check_db


