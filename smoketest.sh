#!/bin/bash

PORT=5001
BASE_URL="http://localhost:$PORT"

echo "▶️ Testing root endpoint..."
curl -s $BASE_URL | jq .

echo "▶️ Creating boxer Boxer1..."
curl -s -X POST $BASE_URL/boxer -H "Content-Type: application/json" -d '{"name":"Boxer1"}' | jq .

echo "▶️ Creating boxer Boxer2..."
curl -s -X POST $BASE_URL/boxer -H "Content-Type: application/json" -d '{"name":"Boxer2"}' | jq .

echo "▶️ Trying to create a third boxer (should fail)..."
curl -s -X POST $BASE_URL/boxer -H "Content-Type: application/json" -d '{"name":"Boxer3"}' | jq .

echo "▶️ Getting all boxers..."
curl -s $BASE_URL/boxers | jq .

echo "▶️ Making them fight..."
curl -s -X POST $BASE_URL/fight | jq .

echo "▶️ Deleting boxer Boxer1..."
curl -s -X DELETE $BASE_URL/boxer -H "Content-Type: application/json" -d '{"name":"Boxer1"}' | jq .

echo "▶️ Getting all boxers after deletion..."
curl -s $BASE_URL/boxers | jq .

echo "✅ Smoketest complete."

