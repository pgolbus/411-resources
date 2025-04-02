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

add_boxer() {
    name=$1
    weight=$2
    height=$3
    reach=$4
    age=$5

    echo "Adding boxer ($name - $weight, $height) to the gym..."
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

    echo "Deleting boxer ($boxer_id)..."
    response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer deleted successfully ($boxer_id)."
    else
        echo "Failed to delete boxer ($boxer_id)."
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
    response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$boxer_name")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer retrieved successfully by name ($boxer_name)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Boxer JSON (NAME $boxer_name):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get boxer by name ($boxer_name)."
        exit 1
    fi
}

bout() {
    echo "Starting a bout..."
    curl -s -X GET "$BASE_URL/fight" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Bout started successfully."
    else
        echo "Failed to start bout."
        exit 1
    fi
}

clear_boxers() {
    echo "Clearing ring..."
    response=$(curl -s -X POST "$BASE_URL/clear-boxers")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Ring cleared successfully"
    else
        echo "Failed to clear ring."
        exit 1
    fi
}

enter_ring() {
    boxer_name=$1

    echo "Adding boxer to ring: $boxer_name..."
    response=$(curl -s -X POST "$BASE_URL/enter_ring" \
        -H "Content-Type: application/json" \
        -d "{\"boxer_name\":\"$boxer_name}")
    
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer added to ring successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Boxer JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to add boxer to ring."
        exit 1
    fi
}

get_boxers() {
    echo "Retrieving all boxers from ring..."
    response=$(curl -s -X GET "$BASE_URL/get-boxers")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "All boxers retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Songs JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to retrieve all boxers from ring."
        exit 1
    fi
}

get_leaderboard() {
    echo "Getting boxer leaderboard sorted by wins or win_pct..."
    response=$(curl -s -X GET "$BASE_URL/leaderboard")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxers leaderboard retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Leaderboard JSON (sorted by play count):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get song leaderboard."
        exit 1
    fi
}

# Initialize the database
sqlite3 db/boxing.db < sql/init_db.sql

# Health checks
check_health
check_db

# Create boxers
add_boxer "John Cena" 200 180 20.0 45
add_boxer "Malcolm Majors" 220 185 15.0 30
add_boxer "Randy William" 205 170 14.0 35
add_boxer "Philip White" 220 185 22.0 30
add_boxer "Fred Armisen" 200 190 23.0 50

delete_boxer 1
get_boxer_by_id 2
get_boxer_by_name "Randy William"

enter_ring "John Cena"
enter_ring "Malcolm Majors"
enter_ring "Philip White"
enter_ring "Fred Armisen"
get_boxers

clear_boxers

enter_ring "Malcolm Majors"
enter_ring "Philip White"
bout
get_boxers

get_leaderboard

echo "All tests passed!"