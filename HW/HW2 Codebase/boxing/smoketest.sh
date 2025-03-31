#!/bin/bash

# Boxing API Smoketest
# Version 2.2 - Verified working version

BASE_URL="http://localhost:5001/api"
ECHO_JSON=false

# Parse arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

##############################################
# Helper Functions
##############################################

show_json() {
  [ "$ECHO_JSON" = true ] && echo "$1" | jq .
}

check_success() {
  echo "$1" | grep -q '"status": "success"'
}

print_header() {
  echo ""
  echo "=== $1 ==="
}

##############################################
# Health Checks
##############################################

check_health() {
  print_header "Health Check"
  response=$(curl -s -X GET "$BASE_URL/health")
  if check_success "$response"; then
    echo "Service Healthy"
    show_json "$response"
  else
    echo "Health Check Failed"
    show_json "$response"
    exit 1
  fi
}

check_db() {
  print_header "Database Check"
  response=$(curl -s -X GET "$BASE_URL/db-check")
  if check_success "$response"; then
    echo "Database Healthy"
    show_json "$response"
  else
    echo "Database Check Failed"
    show_json "$response"
    exit 1
  fi
}

##############################################
# Boxer Management
##############################################

create_boxer() {
  local name=$1 weight=$2 height=$3 reach=$4 age=$5
  print_header "Creating Boxer: $name"
  
  json_data=$(jq -n \
    --arg name "$name" \
    --argjson weight "$weight" \
    --argjson height "$height" \
    --argjson reach "$reach" \
    --argjson age "$age" \
    '{name: $name, weight: $weight, height: $height, reach: $reach, age: $age}')
  
  response=$(curl -s -X POST "$BASE_URL/add-boxer" \
    -H "Content-Type: application/json" \
    -d "$json_data")
  
  if check_success "$response"; then
    echo "Boxer Created"
    show_json "$response"
  elif echo "$response" | grep -q "already exists"; then
    echo "Boxer Exists (Skipping)"
    show_json "$response"
  else
    echo "Creation Failed"
    show_json "$response"
    exit 1
  fi
}

get_boxer_by_id() {
  local id=$1
  print_header "Getting Boxer ID $id"
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$id")
  
  if check_success "$response"; then
    echo "Boxer Found"
    show_json "$response"
  else
    echo "Boxer Not Found"
    show_json "$response"
    exit 1
  fi
}

##############################################
# Ring Operations
##############################################

enter_ring() {
  local name=$1
  print_header "Entering Ring: $name"
  
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\"}")
  
  if check_success "$response"; then
    echo "Boxer Entered"
    show_json "$response"
  else
    echo "Entry Failed"
    show_json "$response"
    exit 1
  fi
}

start_fight() {
  print_header "Starting Fight"
  response=$(curl -s -X GET "$BASE_URL/fight")
  
  if check_success "$response"; then
    winner=$(echo "$response" | jq -r '.winner')
    echo "Winner: $winner"
    show_json "$response"
  else
    echo "Fight Failed"
    show_json "$response"
    exit 1
  fi
}

clear_ring() {
  print_header "Clearing Ring"
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  
  if check_success "$response"; then
    echo "Ring Cleared"
    show_json "$response"
  else
    echo "Clear Failed"
    show_json "$response"
    exit 1
  fi
}

get_ring_boxers() {
  print_header "Current Ring Boxers"
  response=$(curl -s -X GET "$BASE_URL/get-boxers")
  
  if check_success "$response"; then
    count=$(echo "$response" | jq '.boxers | length')
    echo "Boxers in Ring: $count"
    show_json "$response"
  else
    echo "Retrieval Failed"
    show_json "$response"
    exit 1
  fi
}

##############################################
# Leaderboard
##############################################

get_leaderboard() {
  local sort=${1:-wins}
  print_header "Leaderboard ($sort)"
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort")
  
  if check_success "$response"; then
    echo "Top Boxers:"
    # Display the leaderboard in a readable table format
    echo "$response" | jq -r '.leaderboard[] | "\(.name) - Wins: \(.wins), Win %: \(.win_pct), Fights: \(.fights)"'
    echo ""
    show_json "$response"  # Still show full JSON if --echo-json is set
  else
    echo "Leaderboard Failed"
    show_json "$response"
    exit 1
  fi
}

##############################################
# Main Test Flow
##############################################

echo ""
echo "Starting Boxing API Smoketest..."
echo "================================="

# Initial checks
check_health
check_db
clear_ring

# Boxer tests
create_boxer "Muhammad Ali" 125 191 78 32
create_boxer "Mike Tyson" 126 178 71 30
create_boxer "Sugar Ray Leonard" 125 173 74 33

# Boxer operations
get_boxer_by_id 1
get_boxer_by_id 2
get_boxer_by_id 3

# Ring operations
enter_ring "Muhammad Ali"
enter_ring "Mike Tyson"
get_ring_boxers
start_fight
clear_ring

# Leaderboard
get_leaderboard wins
get_leaderboard win_pct

echo "================================="
echo "All Smoke Tests Passed Successfully"
echo ""