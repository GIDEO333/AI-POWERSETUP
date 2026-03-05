#!/usr/bin/env python3
import json
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 remove_mcp.py <mcp_server_name>")
        sys.exit(1)

    server_name = sys.argv[1]
    config_path = os.path.expanduser("~/.gemini/antigravity/mcp_config.json")

    if not os.path.exists(config_path):
        print(f"Error: MCP config file not found at {config_path}")
        sys.exit(1)

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON from config file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error reading config file: {e}")
        sys.exit(1)
        
    mcp_servers = config.get("mcpServers", {})

    if server_name in mcp_servers:
        print(f"Removing '{server_name}' from the MCP configuration...")
        del mcp_servers[server_name]
        
        config["mcpServers"] = mcp_servers
        
        try:
             with open(config_path, 'w') as f:
                 json.dump(config, f, indent=2)
                 f.write('\n') # Add trailing newline
             print(f"✅ Successfully removed '{server_name}'.")
        except Exception as e:
            print(f"Error writing to config file: {e}")
            sys.exit(1)
    else:
        print(f"⚠️  MCP Server '{server_name}' not found in configuration.")
        print(f"Currently configured servers: {', '.join(mcp_servers.keys())}")

if __name__ == "__main__":
    main()
