#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Check service health
check_health() {
  echo "🩺 Checking service health..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "✅ Service is healthy."
  else
    echo "❌ Health check failed."
    exit 1
  fi
}

# Create a boxer with debug logging
create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "🥊 Creating boxer: $name..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")

  echo "📬 Server response for boxer '$name':"
  echo "$response"

  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "✅ Boxer '$name' created successfully."
  else
    echo "❌ Failed to create boxer '$name'."
    exit 1
  fi
}

# Enter ring
enter_ring() {
  name=$1

  echo "🚪 Entering boxer '$name' into the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\"}")
  echo "$response"

  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "✅ Boxer '$name' entered the ring."
  else
    echo "❌ Failed to enter boxer '$name' into the ring."
    exit 1
  fi
}

# Trigger fight
start_fight() {
  echo "🔥 Starting a fight..."
  response=$(curl -s -X GET "$BASE_URL/fight")
  echo "$response"

  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "🥇 Fight completed successfully."
  else
    echo "❌ Fight failed."
    exit 1
  fi
}

# Get leaderboard
get_leaderboard() {
  echo "📊 Retrieving leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  echo "$response"

  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "📈 Leaderboard fetched."
  else
    echo "❌ Failed to retrieve leaderboard."
    exit 1
  fi
}

# Clear the ring
clear_ring() {
  echo "🧹 Clearing the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  echo "$response"

  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "✅ Ring cleared."
  else
    echo "❌ Failed to clear the ring."
    exit 1
  fi
}

# ===== Main Flow =====

check_health

# Add unique timestamp to names to avoid duplication error
timestamp=$(date +%s)
boxer1="Ali_$timestamp"
boxer2="Tyson_$timestamp"

create_boxer "$boxer1" 150 180 75.0 30
create_boxer "$boxer2" 160 175 72.0 28

enter_ring "$boxer1"
enter_ring "$boxer2"
start_fight
get_leaderboard
clear_ring

echo ""
echo "✅✅✅ All boxing smoketests passed successfully!"
