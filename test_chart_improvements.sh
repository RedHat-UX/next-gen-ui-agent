#!/bin/bash

echo "Testing Chart Component Improvements"
echo "====================================="
echo ""

BASE_URL="http://localhost:8000"

echo "Test 1: Line chart with explicit request"
echo "-----------------------------------------"
curl -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me a line chart of Toy Story movie ratings over time"}' \
  | jq '.'
echo ""
echo ""

echo "Test 2: Bar chart comparison"
echo "-----------------------------"
curl -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a bar chart comparing Toy Story movie data"}' \
  | jq '.'
echo ""
echo ""

echo "Test 3: Simple card (non-chart)"
echo "--------------------------------"
curl -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me details about Toy Story in a card"}' \
  | jq '.'
echo ""
echo ""

echo "Test 4: Health check"
echo "--------------------"
curl -X GET "$BASE_URL/health" | jq '.'
echo ""

echo "====================================="
echo "Testing complete!"

