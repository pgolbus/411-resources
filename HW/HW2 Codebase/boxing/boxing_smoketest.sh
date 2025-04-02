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
# Add/Remove Boxers
#
##########################################################

add_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "adding boxer..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\", \"weight\": $weight, \"height\": $height, \"reach\": $reach, \"age\": $age}")


  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer added successfully."
  else
    echo "Failed to add boxer."
    exit 1
  fi
}

delete_boxer_by_id() {
id=$1

  echo "Deleting boxer by ID..."
  response=$(curl -s -X DELETE "$BASE_URL/get-boxer-by-id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer successfully deleted by ID."
  else
    echo "Failed to delete boxer by ID."
    exit 1
  fi
}



############################################################
#
# Get boxers
#
############################################################

get_boxer_by_id() {
id=$1

  echo "Entering boxer in ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer successfully retrieved by ID."
  else
    echo "Failed to retrieve boxer by ID."
    exit 1
  fi
}

get_boxer_by_name() {
name=$1

  echo "Entering boxer in ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer successfully retrieved by name."
  else
    echo "Failed to retrieve boxer by name."
    exit 1
  fi
}

get_boxers_in_ring() {

  echo "Retrieving boxers in ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers in ring successfully retrieved."
  else
    echo "Failed to retrieve boxers in ring."
    exit 1
  fi
}





############################################################
#
# Fight Boxers
#
############################################################

trigger_fight() {
  echo "Initiating fight between two boxers..."
  response=$(curl -s -X GET "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight successfully initiated."
  else
    echo "Failed to initiate fight."
    exit 1
  fi
}



enter_ring() {
name=$1

  echo "Entering boxer in ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\"}")


  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer successfully entered in ring."
  else
    echo "Failed to enter boxer in ring."
    exit 1
  fi
}


clear_ring() {

  echo "Clearing ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")


  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring successfully cleared."
  else
    echo "Failed to clear ring."
    exit 1
  fi
}

############################################################                    
#                                                                              
# Leaderboard                                                                  
#                                                                               
############################################################  

get_leaderboard() {

  echo "Retrieving leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/get-leaderboard")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard successfully retrieved."
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

# create boxers
create_boxer "smoketestboxer1" 200 150 75.0 35
create_boxer "smoketestboxer2" 100 250 75.5 30



# get boxer by name
get_boxer_by_name "smoketestboxer1"

# get boxer by ID
get_boxer_by_id 1

# Place boxers in ring
enter_ring "smoketestboxer1"
enter_ring "smoketestboxer2"


# check ring state
get_boxers_in_ring

# trigger fight
trigger_fight

# clear ring
clear_ring

# get leaderboard
get_leaderboard

# delete boxers
delete_boxer_by_id 1
delete_boxer_by_id 2

echo "All boxing tests passed successfully!"
