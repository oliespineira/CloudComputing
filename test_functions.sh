#!/bin/bash

# Test script for Azure Functions
# Usage: ./test_functions.sh [local|deployed]

MODE=${1:-local}

if [ "$MODE" == "local" ]; then
    BASE_URL="http://localhost:7071/api"
    echo "🧪 Testing Azure Functions LOCALLY"
    echo "Make sure functions are running: cd backend && func start"
    echo ""
elif [ "$MODE" == "deployed" ]; then
    BASE_URL="YOUR_DEPLOYED_FUNCTION_URL_HERE/api"
    echo "🧪 Testing Azure Functions in AZURE"
    echo "Update BASE_URL in this script with your deployed function URL"
    echo ""
else
    echo "Usage: ./test_functions.sh [local|deployed]"
    exit 1
fi

echo "=========================================="
echo "Test 1: RegisterMeal"
echo "=========================================="

curl -X POST "${BASE_URL}/RegisterMeal" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurantName": "Test Restaurant",
    "dishName": "Test Pizza",
    "description": "A test pizza",
    "price": 12.99,
    "prepTime": 25,
    "area": "Central"
  }' \
  -w "\nStatus: %{http_code}\n" \
  | python3 -m json.tool

echo ""
echo "=========================================="
echo "Test 2: RegisterMeal (Missing Fields - Should Fail)"
echo "=========================================="

curl -X POST "${BASE_URL}/RegisterMeal" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurantName": "Test Restaurant",
    "dishName": "Test Pizza"
  }' \
  -w "\nStatus: %{http_code}\n" \
  | python3 -m json.tool

echo ""
echo "=========================================="
echo "Test 3: RegisterMeal (Invalid JSON - Should Fail)"
echo "=========================================="

curl -X POST "${BASE_URL}/RegisterMeal" \
  -H "Content-Type: application/json" \
  -d 'invalid json' \
  -w "\nStatus: %{http_code}\n" \
  | python3 -m json.tool

echo ""
echo "✅ Testing complete!"

