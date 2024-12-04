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
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
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
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal - $cuisine, $price, $difficulty) to the battle..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

# Comment: Not sure if this is correct
# Function to get the leaderboard sorted by wins/win_pct
get_leaderboard() {
  sort_by=$1

  echo "Getting meal leaderboard sorted by wins/win_pct..."
  response=$(curl -s -X GET "$BASE_URL/meal-leaderboard?sort=$sort_by")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      if ["$sort_by" = "wins"]; then
        echo "Leaderboard JSON (sorted by wins):"
      else
        echo "Leaderboard JSON (sorted by win_pct):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal leaderboard."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-from-catalog-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-from-catalog-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    exit 1
  fi
}

############################################################
#
# Battle Management
#
############################################################

prep_combatant() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Prepping meal to battle: $meal - $cuisine ($price, $difficulty)..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":\"$price\", \"difficulty\":$difficulty}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added to battle successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add meal to battle."
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing combatants list..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants list cleared successfully."
  else
    echo "Failed to clear combatants list."
    exit 1
  fi
}

get_combatants() {
  echo "Retrieving all combatants from combatants list..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants-in-battle-list")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all combatants from battle list."
    exit 1
  fi
}

get_battle_score() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$3

  echo "Retrieving battle score by Meal's attributes ($meal,$cusine,$price,$difficulty)..."
  response=$(curl -s -X GET "$BASE_URL/get-battle-score/$meal")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle score retrieved successfully by meal's attributes."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Score JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve battle score by meal's attributes."
    exit 1
  fi
}

battle() {
  echo "Conducting battle..."
  response=$(curl -s -X GET "$BASE_URL/battle")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle conducted successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to conduct battle."
    exit 1
  fi
}


# Health checks
check_health
check_db

# Create meals
create_meal "Meal A" "Cuisine A" 1 "LOW"
create_meal "Meal B" "Cuisine B" 3 "LOW"
create_meal "Meal C" "Cuisine C" 5 "MED"
create_meal "Meal D" "Cuisine D" 7 "MED"
create_meal "Meal E" "Cuisine E" 9 "HIGH"

delete_meal_by_id 1

get_meal_by_id 2
get_meal_by_name "Meal E"

prep_combatant "Meal A" "Cuisine A" 1 "LOW"
prep_combatant "Meal B" "Cuisine B" 3 "LOW"

get_combatants
battle
get_leaderboard "wins"

clear_combatants

get_combatants
get_leaderboard "wins"

prep_combatant "Meal C" "Cuisine C" 5 "MED"
prep_combatant "Meal E" "Cuisine E" 9 "HIGH"

get_battle_score "Meal A" "Cuisine A" 1 "LOW"
get_battle_score "Meal C" "Cuisine C" 5 "MED"

battle
get_combatants
get_leaderboard "win_pct"

echo "All tests passed successfully!"