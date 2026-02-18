import json
from gemini_client import GeminiClient
from mcp_tool_client import MCPToolClient


SYSTEM_PROMPT = """
You are a professional UK banking assistant for a Cash ISA product.
You help users manage accounts, check balances, and make contributions.
You MUST use tools when performing account actions.
Never invent balances, account details, or contribution results. Always call the appropriate tool to get real data.
"""


class CashISAAgent:

    def __init__(self):
        self.gemini = GeminiClient()
        self.tool_client = MCPToolClient()
        self.gemini.set_tools(TOOLS_SCHEMA)
        self.history = [{"role": "user", "parts": [SYSTEM_PROMPT]}]

    def handle_tool_call(self, tool_call):
        tool_name = tool_call.name
        args = json.loads(tool_call.args)

        result = self.tool_client.call_tool(tool_name, args)

        return {
            "role": "tool",
            "name": tool_name,
            "content": json.dumps(result)
        }

    def chat(self, user_input: str):
        self.history.append({"role": "user", "parts": [user_input]})

        response = self.gemini.chat(self.history)

        if response.candidates[0].content.parts[0].function_call:
            tool_call = response.candidates[0].content.parts[0].function_call
            tool_response = self.handle_tool_call(tool_call)
            self.history.append(tool_response)

            final_response = self.gemini.chat(self.history)
            return final_response.text

        return response.text




TOOLS_SCHEMA = [
    {
        "function_declarations": [
            {
                "name": "get_account_balance",
                "description": "Get the current balance of a Cash ISA account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "string",
                            "description": "The account ID"
                        }
                    },
                    "required": ["account_id"]
                }
            },
            {
                "name": "make_contribution",
                "description": "Make a contribution to a Cash ISA account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string"},
                        "amount": {"type": "number"}
                    },
                    "required": ["account_id", "amount"]
                }
            }
        ]
    }
]
