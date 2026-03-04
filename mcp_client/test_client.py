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






    tool_calls = [
        ("get_user_details", {"user_id": "USR008"}),
        ("create_user", {
            "name": "Edward Nuttall",
            "age": 25,
            "uk_resident": True,
            "crown_servant": False,
            "crown_servant_spouse": False,
        }),
        ("get_all_account_details", {"user_id": "USR008"}),
        ("open_cash_isa", {
            "user_id": "USR008",
            "deposit": 1000.0
        }),
        ("check_contribution_eligibility", {
            "user_id": "USR008"
        }),
        ("check_contribution_amount", {
            "user_id": "USR008",
           
        }),
        ("contribute_to_cash_isa", {
            "user_id": "USR008",
            "account_number": 1007,
            "amount": 500.0
        }),
        ("check_cash_isa_eligibility", {
            "user_id": "USR008"
        }),
    ]

    # Loop through and call each tool
    for tool_name, tool_args in tool_calls:
        print(f"\nCalling tool: {tool_name} with args: {tool_args}")
        try:
            result = await client.call_tool(tool_name, tool_args)
            print("Tool call result:")
            print(result)
        except Exception as e:
            print(f"Error calling tool {tool_name}: {e}")

    # Close client
    await client.close()
    print("Client closed.")


if __name__ == "__main__":
    asyncio.run(main())