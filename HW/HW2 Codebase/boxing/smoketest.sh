#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

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
#Status should be healthy for health check and for db success
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


###############################################
#
# Boxers
#
###############################################


#Function to create a boxer, assigned so we don't need specific names yet
create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Creating boxer ($name)..."
  curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer $name created successfully."
  else
    echo "Failed to create boxer $name."
    exit 1
  fi
}

#Function to delete boxer
delete_boxer() {
  name=$1
  
  echo "Getting boxer ID for $name..."
  boxer_data=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$name")
  echo "Got boxer data: $boxer_data"
  
  # Use a different pattern to get/extract the ID
  boxer_id=$(echo "$boxer_data" | grep -o '"id": *[0-9]*' | grep -o '[0-9]*')
  echo "Boxer ID: $boxer_id"
  
  if [ -z "$boxer_id" ]; then
    echo "Failed to get boxer ID for $name."
    exit 1
  fi
  
  echo "Deleting boxer $name with ID $boxer_id..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  echo "Delete response: $response"
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer $name deleted successfully."
  else
    echo "Failed to delete boxer $name."
    exit 1
  fi
}
#Function to get boxer by ID
get_boxer_by_id() {
  name=$1
  
  echo "Getting boxer ID for $name to retrieve by ID..."
  boxer_data=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$name")
  boxer_id=$(echo "$boxer_data" | grep -o '"id": *[0-9]*' | grep -o '[0-9]*')
  
  if [ -z "$boxer_id" ]; then
    echo "Failed to get boxer ID for $name."
    exit 1
  fi
  
  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID."
    exit 1
  fi
}
#Function to get boxer by name
get_boxer_by_name() {
  name=$1

  echo "Getting boxer by name ($name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer $name retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON:"
      echo "$response" | jq .
    fi
  else  
    echo "Failed to get boxer by name: $name."
    exit 1
  fi
}

############################################################
#
# Ring Management
#
############################################################

#Function to clear boxers from the ring
clear_boxers() {
  echo "Clearing boxers from the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers cleared from ring successfully."
  else
    echo "Failed to clear boxers from ring."
    exit 1
  fi
}
#Function to enter boxer into the ring
enter_ring() {
  name=$1
  
  echo "Entering boxer ($name) into the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\"}")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer ($name) entered the ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to enter boxer into the ring."
    exit 1
  fi
}
#Function to get boxers in the ring
get_boxers_in_ring() {
  echo "Getting boxers in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers in ring retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxers in ring."
    exit 1
  fi
}
#Function to fight
fight() {
  echo "Initiating fight..."
  response=$(curl -s -X GET "$BASE_URL/fight")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight completed successfully."
    winner=$(echo "$response" | grep -o '"winner":"[^"]*"' | cut -d':' -f2 | tr -d '"')
    echo "Winner: $winner"
    if [ "$ECHO_JSON" = true ]; then
      echo "Fight JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to complete fight."
    exit 1
  fi
}

############################################################
#
# Leaderboard
#
############################################################
#Function to get leaderboard
get_leaderboard() {
  sort_by=${1:-wins}  # Default to sorting by wins
  
  echo "Getting leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_by")
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

###############################################
#
# Error Handling Tests
#
###############################################
#Function to test duplicate boxer
test_duplicate_boxer() {
  echo "========== Testing Error: Duplicate Boxer =========="
  
  name="DuplicateTest"
  weight=150
  height=65
  reach=72.0
  age=28
  
  echo "Creating first boxer ($name)..."
  first_response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")
  
  echo "Attempt to create duplicate boxer ($name)..."
  second_response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")
  
  echo "Response: $second_response"
  if echo "$second_response" | grep -q '"status": "error"'; then
    echo "Test passed: Properly rejected duplicate "
  else
    echo "Test failed:  accepted duplicate "
  fi
  
  # Clean up
  boxer_data=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$name")
  boxer_id=$(echo "$boxer_data" | grep -o '"id": *[0-9]*' | grep -o '[0-9]*')
  if [ -n "$boxer_id" ]; then
    curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id" > /dev/null
  fi
}
#Function to test third boxer in ring
test_third_boxer_in_ring() {
  echo "========== Testing Error: Third Boxer in Ring =========="
  
  # Clear the ring  first
  clear_boxers
  
  # Create three boxers
  names=("Dude1" "Dude2" "Dude3")
  
  for name in "${names[@]}"; do
    echo "Creating boxer ($name)..."
    curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
      -d "{\"name\":\"$name\", \"weight\":150, \"height\":65, \"reach\":72, \"age\":28}" > /dev/null
  done
  
  # Add first two boxers to the ring
  curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d "{\"name\":\"Fighter1\"}" > /dev/null
  curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d "{\"name\":\"Fighter2\"}" > /dev/null
  
  # Try to add the third boxer
  echo "Attempting to add third boxer to the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d "{\"name\":\"Fighter3\"}")
  
  echo "Response: $response"
  
  if echo "$response" | grep -q '"status": "error"'; then
    echo "Test passed: Properly rejected third boxer in ring"
  else
    echo "Test failed: accepted third boxer in ring"
  fi


# Clean up
  clear_boxers
  for name in "${names[@]}"; do
    boxer_data=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$name")
    boxer_id=$(echo "$boxer_data" | grep -o '"id": *[0-9]*' | grep -o '[0-9]*')
    if [ -n "$boxer_id" ]; then
      curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id" > /dev/null
    fi
  done
}





#Initialize the database, just kidding the container runs this
#sqlite3 db/boxing.db < sql/init_db.sql

#Health checks
check_health
check_db    

# Boxer Management
#Create the boxers and show it in terminal well
echo "========== Boxer Management =========="
create_boxer "Michelle" 135 58 70.0 30
get_boxer_by_name "Michelle"
get_boxer_by_id "Michelle"


# Ring Management
echo "========== Ring Management =========="
clear_boxers
enter_ring "Michelle"

# Second boxer
name="Wesley"
echo "Checking if boxer '$name' already exists..."
wesley_exists=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$name")
if ! echo "$wesley_exists" | grep -q '"status": "success"'; then
  echo "Creating second boxer ($name)..."
  create_boxer "Wesley" 175 71 76.0 32
fi

enter_ring "Wesley"
get_boxers_in_ring
fight


#Error handling tests
echo "========== Error Handling Tests =========="
test_duplicate_boxer
test_third_boxer_in_ring






# Leaderboard but will not show unless we make the json data true at the top
echo "========== Leaderboard =========="
get_leaderboard
get_leaderboard "win_pct"

# Final cleanup
echo "========== Cleanup =========="
delete_boxer "Michelle"
delete_boxer "Wesley"





echo "doneeee!"