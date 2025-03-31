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


############################################################
#
# Get boxers
#
############################################################


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
