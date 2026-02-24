import asyncio
from client import MCPClient


async def main():
    command = "python"
    args = ["mcp_server/server.py"]

    client = MCPClient(command, args)

    print("Connecting to MCP server...")
    await client.connect()
    print("Connected!\n")

    tools = await client.list_tools()
    print("Available tools:", tools)

    await client.close()
    print("Closed.")


asyncio.run(main())