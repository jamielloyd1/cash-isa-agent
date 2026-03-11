import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


class MCPClient:
    def __init__(self, command: str, args: list[str]):
        self.command = command
        self.args = args
        self.session = None
        self._client_context = None

    async def connect(self):
        server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
        )

        self._client_context = stdio_client(server_params)

        read_stream, write_stream = await self._client_context.__aenter__()
        self.session = ClientSession(read_stream, write_stream)
        await self.session.__aenter__()
        await self.session.initialize()

    async def list_tools(self):
        return await self.session.list_tools()

    async def call_tool(self, name: str, arguments: dict):
        return await self.session.call_tool(name, arguments)

    async def close(self):
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self._client_context:
            await self._client_context.__aexit__(None, None, None)