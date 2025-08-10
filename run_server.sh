#!/bin/bash

# Example script to run the Nautobot MCP Server
# Update the URL and TOKEN variables with your actual values

NAUTOBOT_URL="${NAUTOBOT_URL:-http://localhost:8080}"
NAUTOBOT_TOKEN="${NAUTOBOT_TOKEN:0123456789abcdef0123456789abcdef01234567}"

echo "Starting Nautobot MCP Server..."
echo "URL: $NAUTOBOT_URL"
echo "============================="

python -m nautobot_mcp_server \
    --url "$NAUTOBOT_URL" \
    --token "$NAUTOBOT_TOKEN" \
    --debug
