#!/bin/bash

# Smoke test script: tests basic functionality of the boxing app
# 
# This script tests the following features:
# 1. Service health check
# 2. Database connection verification
# 3. Adding a boxer
# 4. Retrieving boxer list
# 5. Deleting a boxer

# API endpoint URL
BASE_URL="http://localhost:5002/api"

# Flag to control JSON output
ECHO_JSON=false

# Parse command line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

# Health check function
check_health() {
  echo "Checking service status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is running normally."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Database connection check function
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database connection check failed."
    exit 1
  fi
}

# Function to clear the ring
clear_ring() {
  echo "Clearing the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
    
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
    
  else
    echo "Failed to clear ring."
    exit 1
  fi
}

# Function to add a boxer
add_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5
  
  echo "Adding boxer: $name ($weight kg, $height cm, $reach inches, $age years old)..."
  
  curl -s -X POST "$BASE_URL/add-boxer" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}" | grep -q '"status": "success"'
  
  if [ $? -eq 0 ]; then
    echo "Boxer added successfully."
  else
    echo "Failed to add boxer."
    exit 1
  fi
}

# Function to get all boxers
get_all_boxers() {
  echo "Retrieving all boxers..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")
  
  if echo "$response" | grep -q '"boxers"'; then
    echo "Successfully retrieved all boxers."
    
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer list JSON:"
      echo "$response" | jq .
    fi
    
    # Extract test boxer ID
    boxer_id=$(echo "$response" | grep -o '"id": [0-9]*' | grep -o '[0-9]*' | head -1)
    if [ -n "$boxer_id" ]; then
      echo "Test boxer ID: $boxer_id"
      return $boxer_id
    else
      echo "Could not find boxer ID."
      return 0
    fi
  else
    echo "Failed to retrieve boxers."
    exit 1
  fi
}

# Function to add boxer to ring
enter_ring() {
  name=$1
  
  echo "Adding boxer to ring: $name..."
  
  curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\"}" | grep -q '"status": "success"'
  
  if [ $? -eq 0 ]; then
    echo "Boxer entered the ring successfully."
  else
    echo "Failed to enter ring."
    exit 1
  fi
}

# Function to delete a boxer
delete_boxer() {
  boxer_id=$1
  
  echo "Deleting boxer (ID: $boxer_id)..."
  curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id" | grep -q '"status": "success"'
  
  if [ $? -eq 0 ]; then
    echo "Boxer deleted successfully."
  else
    echo "Failed to delete boxer."
    exit 1
  fi
}

# Initialize the database
sqlite3 db/boxing.db < sql/init_db.sql

# Wait for server startup
echo "Waiting for server startup..."
sleep 3

# Test 1: Health check
echo -e "\nTest 1: Service health check"
check_health

# Test 2: Database connection check
echo -e "\nTest 2: Database connection check"
check_db

# Test 3: Clear ring
echo -e "\nTest 3: Clear ring"
clear_ring

# Generate unique boxer name with timestamp
BOXER_NAME="Test Boxer $(date +%s)"

# Test 4: Add boxer
echo -e "\nTest 4: Add boxer"
add_boxer "$BOXER_NAME" 180 175 70 25

# Test 5: Enter ring
echo -e "\nTest 5: Enter ring"
enter_ring "$BOXER_NAME"

# Test 6: Get boxers
echo -e "\nTest 6: Get boxers"
get_all_boxers
boxer_id=$?

if [ $boxer_id -gt 0 ]; then
  echo "Found test boxer with ID $boxer_id"
  
  # Test 7: Delete boxer
  echo -e "\nTest 7: Delete boxer"
  delete_boxer $boxer_id
else
  echo "Could not find test boxer ID, skipping deletion test."
  exit 1
fi

echo "All tests completed successfully!"