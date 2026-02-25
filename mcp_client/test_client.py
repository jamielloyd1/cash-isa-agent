import asyncio
from client import MCPClient

async def main():
    # Command to run your MCP server
    command = "python"
    args = ["mcp_server/server.py"]

    print("Connecting to MCP server...")
    client = MCPClient(command, args)
    await client.connect()
    print("Connected!")

    # List available tools
    tools = await client.list_tools()
    print("\nAvailable tools:")
    for tool in tools.tools:
        print(f"- {tool.name}: {tool.description}")

    # --- Tool call example ---
    # Fill in the tool name and arguments
    tool_name = "get_all_account_details"  # e.g., "get_user_details"
    tool_args = {
        # Fill in the required arguments for this tool
        "user_id": "USR008"
    }

    print(f"\nCalling tool: {tool_name} with args: {tool_args}")
    try:
        result = await client.call_tool(tool_name, tool_args)
        print("Tool call result:")
        print(result)
    except Exception as e:
        print(f"Error calling tool: {e}")

    # Close client
    await client.close()
    print("Client closed.")

if __name__ == "__main__":
    asyncio.run(main())