#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://127.0.0.1:5002/api"

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

# Checks the health of the service
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

# Checks the database connection
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

# Creates a new boxer.
create_boxer() {
    name=$1
    weight=$2
    height=$3
    reach=$4
    age=$5

echo "Creating boxer $name ($weight lbs, $height inches, $reach reach, $age years old) ..."
curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer created successfully."
  else
    echo "Failed to create boxer."
    exit 1
  fi
}

# Deletes boxer associated with boxer_id.
delete_boxer_using_id() {
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

# Returns boxers in the ring.
get_boxers() {
  echo "Getting boxers in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers") # based on "get-all-songs-from-catalog"
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get Boxers."
    exit 1
  fi
}

# Finds and returns boxers using boxer_id.
get_boxer_by_id() {
  boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id") # based on "get-song-from-catalog-by-id" 
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

# Finds and returns boxer using name.
get_boxer_by_name() {
  name=$1

  echo "Getting boxer by name (Name: '$name')..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$(echo $name | sed 's/ /%20/g')") 
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name."
    exit 1
  fi
}

############################################################
#
# Ring Management
#
############################################################

# Enters boxers to the ring.
enter_ring() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding boxer to ring: $name..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer added to ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add boxer to the ring."
    exit 1
  fi
}

# Clears boxers from the ring.
clear_ring() {
  echo "Clearing boxers from the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers cleared successfully."
  else
    echo "Failed to clear boxers from the ring."
    exit 1
  fi
}


############################################################
#
# Start fight
#
############################################################

fight() {
  echo "Starting the fight..."
  response=$(curl -s -X POST "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "The fight has begun."
  else
    echo "Failed to start the fight."
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

# Returns the boxer leaderboard sorted by wins or win_pct
get_boxer_leaderboard() {
  echo "Getting boxer leaderboard sorted by wins or win percentage..."
  sort_by=${1:-wins} 

  if [[ "$sort_by" != "wins" && "$sort_by" != "win_pct" ]]; then
    echo "Invalid sort parameter: '$sort_by'. Must be 'wins' or 'win_pct'."
    exit 1
  fi

  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_by")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by $sort_by):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer leaderboard."
    exit 1
  fi
}

##############################
#                            #
# Check connectivity         #
#                            #
##############################

# Initialize the database
sqlite3 boxing_db/boxers.db < sql/init_db.sql

# Health checks
check_health
check_db


##############################
#                            #
# Testing                    #
#                            #
##############################

# Test creating boxers.
create_boxer "Kiki" 135 64 64 38
create_boxer "Bouba" 132 65 65.8 27

# Test deleting boxers using boxer ID.
delete_boxer_by_id 3

# Test get_boxer
get_boxer_by_id 2
get_boxer_by_name "Kiki"

# Tests to enter boxers and clear ring.
enter_ring "Kiki" 135 64 64 38
enter_ring "Bouba" 132 65 65.8 27
get_boxers
clear_ring

# Test to start a fight.
enter_ring  "Kiki" 135 64 64 38
enter_ring "Bouba" 132 65 65.8 27
fight

# Test to get leaderboard.
get_boxer_leaderboard # default 'win'. 
get_boxer_leaderboard win_pct 

echo "All tests passed!"
