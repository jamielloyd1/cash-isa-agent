# Cash ISA Agent (Gemini-based)

## Overview

The **Cash ISA Agent** is an AI-powered client that interacts with the **MCP server** to provide Cash ISA guidance to users.  
It uses the **Gemini model** to interpret user queries, decide which MCP tools to call, and generate human-readable responses.

Responsibilities:
- Accept user input (questions, requests, or commands).  
- Call MCP server tools for authoritative information.  
- Format the output as natural language responses.  
- Never store sensitive data locally.  

---

## Folder Structure

agents/cash-isa-agent/
├── agent.py # Main agent logic
├── prompts.py # Prompt templates for the Gemini model
├── config.yaml # Configuration for agent (MCP server URL, API keys)
├── services_examples.txt # Optional reference for service logic usage
├── tools_examples.txt # Optional reference for tool usage
├── README.md # This file
└── pyproject.toml # Python project dependencies


---

## Key Concepts

### 1. Agent Logic (`agent.py`)
- Receives user queries.
- Parses intents.
- Determines which **MCP tools** to call.
- Uses Gemini to format responses in natural language.

Example flow:
User Input → Agent → MCP Tool → Service → Repository → Data


### 2. Prompts (`prompts.py`)
- Stores structured templates for Gemini queries.
- Ensures the model asks for only the information it needs.
- Example:
```python
CASH_ISA_PROMPT = """
Given the user's eligibility and allowance data from the MCP server, explain in plain English:
- Whether the user can open a new Cash ISA.
- How much they can contribute.
"""
3. Configuration (config.yaml)
Stores MCP server endpoint, API keys, thresholds, and other runtime settings.

Keeps secrets and URLs out of code.

Example Usage
from agent import CashISAAgent

agent = CashISAAgent(mcp_server_url="http://localhost:8000")

user_query = "Can I open a new Cash ISA and how much can I contribute?"
response = agent.handle_user_query(user_query, user_id="u123")

print(response)
# Output (example):
# "You are eligible to open a new Cash ISA. You can contribute up to £16,500 this tax year."