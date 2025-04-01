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

add_boxer() {

}

add_boxer_errors() {

}

delete_boxer_by_id() {

}

get_all_boxers() {
  echo "Getting all boxers in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxers in ring."
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

  echo "Getting boxer by Name ($boxer_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$(echo $boxer_name | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by Name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by Name ($boxer_name)."
    exit 1
  fi
}

##########################################################
#
# Ring Management
#
##########################################################

enter_ring_too_many() {
  
  echo "Test adding more than two boxer to ring..."

  # first add 3 boxer for test
  add_boxer "BoxerA_1" 160 70 72.5 25
  add_boxer "BoxerB_1" 160 68 70.0 30

  add_boxer "BoxerC_1" 160 68 70.0 30

  boxer_name="BoxerC_1"
  # clear boxers
  curl -s -X POST "$BASE_URL/clear-boxers" > /dev/null

  curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\":\"BoxerA_1\"}" > /dev/null
  
  curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\":\"BoxerB_1\"}" > /dev/null

  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\":\"$boxer_name\"}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Error: Boxer entered ring  by Name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
    exit 1
  else
    echo "The server successfully reject Entering ring boxer by Name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
    
  fi
}

enter_ring() {
  boxer_name=$1

  echo "Let boxer with Name ($boxer_name) enter ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\":\"$boxer_name\"}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer entered ring successfully by Name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to enter ring boxer by Name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

fight() {
  
}



# Initialize the database
sqlite3 data/boxing.db < sql/init_db.sql
# clear the boxers in the ring before test
curl -s -X POST "$BASE_URL/clear-boxers" > /dev/null

# Health checks
check_health
check_db
add_boxer "New Boxer" 170 71 73.0 28
add_boxer_errors "Light Boxer" 120 65 68.0 22
add_boxer_errors "Short Boxer" 150 0 70.0 27
add_boxer_errors "Short Reach Boxer" 165 72 0 29
add_boxer_errors "Old boxer" 180 73 74.0 41
add_boxer_errors "Young boxer" 180 73 74.0 11
# duplicate name
add_boxer_errors "New Boxer" 170 71 73.0 28

# add more boxer
add_boxer "BoxerA" 160 70 72.5 25
add_boxer "BoxerB" 160 68 70.0 30

# get boxer by name
get_boxer_by_name "BoxerA"
get_boxer_by_name "BoxerB"
get_boxer_by_name "New Boxer"

# get boxer by ID
get_boxer_by_id 1
get_boxer_by_id 2
get_boxer_by_id 3


# get all boxers in ring
get_all_boxers


# enter ring and fight
enter_ring "BoxerA"
enter_ring "BoxerB"

# get all boxers in ring
get_all_boxers

# fight
fight

# delete boxer by ID
delete_boxer_by_id 1

# test too many boxers entered
enter_ring_too_many

echo "All tests passed successfully!"
