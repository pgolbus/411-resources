BASE_URL="http://localhost:1000/api"
fail_count=0

function test_endpoint {
    local description="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"

    echo "Testing: $description"
    if [[ "$method" == "GET" ]]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    elif [[ "$method" == "POST" ]]; then
        response=$(curl -s -X POST -H "Content-Type: application/json" -d "$data" -w "\n%{http_code}" "$BASE_URL$endpoint")
    elif [[ "$method" == "DELETE" ]]; then
        response=$(curl -s -X DELETE -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        echo "Unsupported HTTP method: $method"
        return 1
    fi

    http_body=$(echo "$response" | sed '$d')
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq "$expected_status" ]; then
        echo "PASS (HTTP $http_code)"
    else
        echo "FAIL: Expected HTTP $expected_status but got HTTP $http_code"
        echo "Response body: $http_body"
        fail_count=$((fail_count + 1))
    fi
}

test_endpoint "Health Check" "GET" "/health" "" 200

test_endpoint "Database Check" "GET" "/db-check" "" 200

test_boxer_name="Test Boxer"
test_boxer_payload=$(cat <<EOF
{
  "name": "$test_boxer_name",
  "weight": 70,
  "height": 175,
  "reach": 70.5,
  "age": 25
}
EOF
)

test_endpoint "Get Boxer That Doesn't Exist By Name" "GET" "/get-boxer-by-name/${encoded_boxer_name}" "" 404

test_endpoint "Get Nonexistent ID" "GET" "/get-boxer-by-id/999" "" 500

test_endpoint "Delete Nonexistent ID" "GET" "/api/delete-boxer/999" "" 404


test_endpoint "Add Boxer With Invalid Weight" "POST" "/add-boxer" "$test_boxer_payload" 500

test_boxer_payload=$(cat <<EOF
{
  "name": "$test_boxer_name",
  "weight": 125,
  "height": 175,
  "reach": 70.5,
  "age": 1
}
EOF
)

test_endpoint "Add Boxer With Invalid Age" "POST" "/add-boxer" "$test_boxer_payload" 500

test_boxer_payload=$(cat <<EOF
{
  "name": "$test_boxer_name",
  "weight": 125,
  "height": 175,
  "reach": 70.5,
  "age":""
}
EOF
)

test_endpoint "Add Boxer With Incorrect JSON Inputs" "POST" "/add-boxer" "$test_boxer_payload" 400

test_boxer_payload=$(cat <<EOF
{
  "name": "$test_boxer_name",
  "weight": 125,
  "height": 175,
  "reach": 70.5,
  "age": 19
  }
EOF
)

test_endpoint "Add Boxer With Valid Parameters" "POST" "/add-boxer" "$test_boxer_payload" 201


encoded_boxer_name=$(echo "$test_boxer_name" | sed 's/ /%20/g')
test_endpoint "Get Boxer by Name" "GET" "/get-boxer-by-name/${encoded_boxer_name}" "" 200


response=$(curl -s "$BASE_URL/get-boxer-by-name/${encoded_boxer_name}")

boxer_id=$(echo "$response" | jq -r '.boxer.id')

if [ -z "$boxer_id" ] || [ "$boxer_id" == "null" ]; then
    echo "Could not retrieve boxer ID. Exiting tests."
    exit 1
fi

test_endpoint "Get Boxer by ID" "GET" "/get-boxer-by-id/$boxer_id" "" 200

enter_ring_payload=$(cat <<EOF
{
  "name": "$test_boxer_name"
}
EOF
)
test_endpoint "Enter Ring" "POST" "/enter-ring" "$enter_ring_payload" 200

test_endpoint "Get Boxers in Ring" "GET" "/get-boxers" "" 200

#test_endpoint "Fight (Expected Success)" "GET" "/fight " "" 200


test_endpoint "Clear Boxers from Ring" "POST" "/clear-boxers" "" 200


test_endpoint "Fight (Not enough people)" "GET" "/fight" "" 400

test_endpoint "Leaderboard (expected success)" "GET" "/leaderboard" "" 200

test_endpoint "Leaderboard with incorrect parameters" "GET" "/leaderboard?sort=w" "" 400


test_endpoint "Delete Boxer" "DELETE" "/delete-boxer/$boxer_id" "" 200

boxer_one_payload=$(cat <<EOF
{
  "name": "Boxer One",
  "weight": 125,
  "height": 175,
  "reach": 70.5,
  "age": 25
}
EOF
)
test_endpoint "Add Boxer One" "POST" "/add-boxer" "$boxer_one_payload" 201

boxer_two_payload=$(cat <<EOF
{
  "name": "Boxer Two",
  "weight": 125,
  "height": 180,
  "reach": 72,
  "age": 28
}
EOF
)
test_endpoint "Add Boxer Two" "POST" "/add-boxer" "$boxer_two_payload" 201

enter_boxer_one_payload='{"name": "Boxer One"}'
test_endpoint "Enter Boxer One into Ring" "POST" "/enter-ring" "$enter_boxer_one_payload" 200

enter_boxer_two_payload='{"name": "Boxer Two"}'
test_endpoint "Enter Boxer Two into Ring" "POST" "/enter-ring" "$enter_boxer_two_payload" 200

test_endpoint "Trigger Fight (expected success)" "GET" "/fight" "" 200

if [ $fail_count -eq 0 ]; then
    echo "All tests passed."
    exit 0
else
    echo "$fail_count test(s) failed."
    exit 1
fi
