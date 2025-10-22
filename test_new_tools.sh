#!/bin/bash

echo "=== Testing New Movie Tools with Charts ==="
echo ""

echo "Test 1: Compare Pixar Movie Ratings (Bar Chart)"
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me a bar chart comparing IMDB ratings of Pixar movies"}' \
  | jq '.response | {title, chartType, dataCount: (.data | length)}'

sleep 2

echo ""
echo "Test 2: Box Office Revenue Comparison (Bar Chart)"
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a bar chart of box office revenue for top Pixar films"}' \
  | jq '.response | {title, chartType, dataCount: (.data | length)}'

sleep 2

echo ""
echo "Test 3: Compare Specific Movies (Line Chart)"
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me a line chart comparing Toy Story, Finding Nemo, and Up ratings"}' \
  | jq '.response | {title, chartType, dataCount: (.data | length)}'

sleep 2

echo ""
echo "Test 4: Budget vs Revenue (Multi-series)"
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Compare budget and revenue for Pixar movies in a chart"}' \
  | jq '.response | {title, chartType, dataCount: (.data | length)}'

echo ""
echo "Test 5: Top Rated Movies (Table or Cards)"
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me all top-rated Pixar movies"}' \
  | jq '.response | {component, title}'

echo ""
echo "=== All Tests Complete ==="

