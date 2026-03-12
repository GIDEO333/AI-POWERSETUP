#!/bin/bash
# FORGE — Switchboard wrapper (macOS)
# Ensures Switchboard runs from $HOME so it finds ~/.switchboard/mcps/
# Includes error handling for graceful failure

set -euo pipefail

# Check if switchboard is installed
if ! command -v switchboard &>/dev/null; then
    # Try finding it in homebrew
    export PATH="/opt/homebrew/bin:$PATH"
    if ! command -v switchboard &>/dev/null; then
        echo '{"jsonrpc":"2.0","id":null,"error":{"code":-32603,"message":"switchboard not found. Run: npm install -g @george5562/switchboard"}}' >&2
        exit 1
    fi
fi

cd "$HOME"

# Run switchboard but filter out non-JSON stdout logs which break the IDE's MCP client
exec switchboard "$@" | grep --line-buffered '^{.*}'
