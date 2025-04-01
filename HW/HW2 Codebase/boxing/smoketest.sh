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
db_check() {
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
# boxer Management
#
##########################################################

add_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5
  

  echo "Adding boxer ($name - $age, $height) to the ring..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")
  echo "$response" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "boxer added successfully."
  else
    echo "Failed to add boxer."
    echo "$response"
    exit 1
  fi
}

delete_boxer() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "boxer deleted successfully by ID ($boxer_id)."
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
    echo "boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "boxer JSON (ID $boxer_id):"
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
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$boxer_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "boxer retrieved successfully by Name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by Name ($boxer_name)."
    exit 1
  fi
}





############################################################
#
# ring Management
#
############################################################

bout() {
  echo "Starting ring fight..."
  response=$(curl -s -X POST "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "fight started successfully."
  else
    echo "Failed to start fight."
    exit 1
  fi

}


clear_boxers() {
  echo "Clearing ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "ring cleared successfully."
  else
    echo "Failed to clear ring."
    exit 1
  fi
}

enter_ring() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding a boxer to the ring: $name - $reach ($age)..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":\"$weight\", \"height\":$height,\"reach\":$reach,\"age\":$age}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "boxer added to ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "boxer JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add boxer to ring."
    exit 1
  fi
}

get_boxers() {
 
  echo "Retrieving boxers: ..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status":'; then
    echo "Boxers retrieved successfully."
  else
    echo "Failed to retrieve boxers."
    exit 1
  fi
}

get_fighting_skills() {
  boxer_id=$1
  echo "Retrieving fighting skills from boxer: $boxer_id ..."
  response=$(curl -s -X GET "$BASE_URL/get-fighting-skills/$boxer_id")

  if echo "$response" | grep -q '"status":'; then
    echo "Boxer's fighting skills retrieved successfully."
  else
    echo "Failed to retrieve boxer's fighting skills."
    exit 1
  fi
}


######################################################
#
# Leaderboard
#
######################################################

# Function to get the boxer leaderboard sorted by win_pct
get_leaderboard() {
  sortfield=$1
  echo "Getting boxer leaderboard sorted by win_pct..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sortfield")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "boxer leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by play count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer leaderboard."
    exit 1
  fi
}

# Initialize the database
sqlite3 db/boxing.db < sql/init_db.sql

# Health checks
check_health
db_check

# Create boxers
add_boxer "Mike" 170 80 12 25
add_boxer "John" 167 72 20 36
add_boxer "Tom" 125 70 12 30
add_boxer "Sam" 190 75 30 40

get_boxers

get_boxer_by_id 1
get_boxer_by_id 2
get_boxer_by_name "Tom"

enter_ring "Mike" 170 80 12 25
enter_ring "John" 167 72 20 36

bout

get_fighting_skills 3

clear_boxers


get_leaderboard

echo "All tests passed successfully!"
