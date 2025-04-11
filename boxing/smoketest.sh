#!/bin/bash

PORT=5001
BASE_URL=http://localhost:$PORT

rm -f boxing/boxing/db/boxers.db

echo "creating boxer 1"
curl -X POST "$BASE_URL/boxers" -H "Content-Type: application/json" -d '{
  "name": "Ali",
  "weight": 180,
  "height": 70,
  "reach": 72.5,
  "age": 28
}'
echo

echo "creating boxer 2"
curl -X POST "$BASE_URL/boxers" -H "Content-Type: application/json" -d '{
  "name": "Tyson",
  "weight": 200,
  "height": 72,
  "reach": 73,
  "age": 30
}'
echo

echo "creating duplicate boxer"
curl -X POST "$BASE_URL/boxers" -H "Content-Type: application/json" -d '{
  "name": "Ali",
  "weight": 185,
  "height": 71,
  "reach": 72,
  "age": 29
}'
echo

echo "creating third boxer"
curl -X POST "$BASE_URL/boxers" -H "Content-Type: application/json" -d '{
  "name": "Fury",
  "weight": 220,
  "height": 76,
  "reach": 80,
  "age": 34
}'
echo

echo "getting all boxers"
curl "$BASE_URL/boxers"
echo

echo "deleting boxer 1"
curl -X DELETE "$BASE_URL/boxers/1"
echo

echo "getting boxers after deletion"
curl "$BASE_URL/boxers"
echo
