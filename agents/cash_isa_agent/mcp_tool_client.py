import requests


class MCPToolClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def call_tool(self, tool_name: str, arguments: dict):
        response = requests.post(
            f"{self.base_url}/tools/{tool_name}",
            json=arguments
        )
        response.raise_for_status()
        return response.json()
