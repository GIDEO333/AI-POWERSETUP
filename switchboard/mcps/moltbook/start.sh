#!/bin/bash
# Moltbook MCP start script (Dynamically reads API key from config)
export NODE_NO_WARNINGS=1
unset DEBUG
unset NODE_ENV

CRED_FILE="$HOME/.config/moltbook/credentials.json"
if [ -f "$CRED_FILE" ]; then
    # Dynamically extract the api_key using grep and sed, avoiding jq dependency
    export MOLTBOOK_API_KEY=$(cat "$CRED_FILE" | grep -o '"api_key": "[^"]*' | grep -o '[^"]*$')
else
    echo '{"jsonrpc":"2.0","id":null,"error":{"code":-32603,"message":"Moltbook credentials not found in ~/.config/moltbook/credentials.json"}}' >&2
    exit 1
fi

# Execute the local bundle
exec node "$HOME/.switchboard/mcps/moltbook/node_modules/moltbook-http-mcp/dist/cli.js" --stdio
