#!/usr/bin/env python
"""Test client for Nautobot MCP Server."""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_nautobot_mcp():
    """Test the Nautobot MCP server functionality."""
    
    # Server configuration - update these values for your environment
    server_params = StdioServerParameters(
        command="python",
        args=[
            "-m", "nautobot_mcp_server",
            "--url", "http://localhost:8080",  # Update with your Nautobot URL
            "--token", "your-api-token-here"   # Update with your API token
        ]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            print("MCP Server initialized successfully!")
            print("=" * 50)
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            print("=" * 50)
            
            # Test 1: List devices
            print("\nTest 1: Listing devices (limit=5)")
            result = await session.call_tool(
                "nautobot_list_devices",
                {"limit": 5}
            )
            print("Response:")
            for content in result:
                if hasattr(content, 'text'):
                    try:
                        data = json.loads(content.text)
                        print(json.dumps(data, indent=2))
                    except:
                        print(content.text)
            
            # Test 2: Get a specific device (if you know an ID or name)
            # Uncomment and update with a real device ID/name to test
            # print("\nTest 2: Getting specific device")
            # result = await session.call_tool(
            #     "nautobot_get_device",
            #     {"device_id": "device-name-or-uuid"}
            # )
            # print("Response:")
            # for content in result:
            #     if hasattr(content, 'text'):
            #         print(content.text)
            
            # Test 3: Create a device (example - will need valid data)
            # Uncomment and update with valid data for your Nautobot instance
            # print("\nTest 3: Creating a device")
            # result = await session.call_tool(
            #     "nautobot_create_device",
            #     {
            #         "name": "test-device-001",
            #         "device_type": "DCS-7280SR-48C6",  # Update with valid device type
            #         "role": "leaf",                     # Update with valid role
            #         "site": "datacenter-1",             # Update with valid site
            #         "status": "active"
            #     }
            # )
            # print("Response:")
            # for content in result:
            #     if hasattr(content, 'text'):
            #         print(content.text)
            
            print("\n" + "=" * 50)
            print("Test completed successfully!")


if __name__ == "__main__":
    print("Starting Nautobot MCP Server test...")
    print("Make sure to update the URL and token in this script!")
    print("=" * 50)
    
    try:
        asyncio.run(test_nautobot_mcp())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()