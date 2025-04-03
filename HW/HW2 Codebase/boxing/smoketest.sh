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
# Song Management
#
##########################################################

create_song() {
  artist=$1
  title=$2
  year=$3
  genre=$4
  duration=$5

  echo "Adding song ($artist - $title, $year) to the playlist..."
  curl -s -X POST "$BASE_URL/create-song" -H "Content-Type: application/json" \
    -d "{\"artist\":\"$artist\", \"title\":\"$title\", \"year\":$year, \"genre\":\"$genre\", \"duration\":$duration}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Song added successfully."
  else
    echo "Failed to add song."
    exit 1
  fi
}

# Initialize the database
sqlite3 db/playlist.db < sql/init_db.sql

# Health checks
check_health
check_db

# Create songs

##create_song "The Beatles" "Hey Jude" 1968 "Rock" 180
##create_song "The Rolling Stones" "Paint It Black" 1966 "Rock" 180
##create_song "The Beatles" "Let It Be" 1970 "Rock" 180
##create_song "Queen" "Bohemian Rhapsody" 1975 "Rock" 180
##create_song "Led Zeppelin" "Stairway to Heaven" 1971 "Rock" 180

echo "All tests passed successfully!"
