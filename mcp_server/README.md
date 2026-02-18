# MCP Server for Cash ISA Platform

## Overview

The **MCP Server** is a standalone microservice that exposes tools for determining Cash ISA eligibility and calculations.  
It is designed to be **stateless** and **reusable** by multiple AI agents (e.g., Gemini-based agents).  

Responsibilities:
- Fetch user and policy data from repositories.
- Convert raw data into typed models.
- Apply business rules via services.
- Return structured results to agents.

---

## Folder Structure

mcp-server/
├── src/
│ ├── server.py # Main MCP server entrypoint
│ ├── tools/ # Tools exposed to agents
│ │ ├── eligibility_tools.py
│ │ └── ...
│ ├── services/ # Business logic (eligibility, allowance calculations)
│ │ ├── eligibility_service.py
│ │ └── ...
│ ├── repositories/ # Data access (users, policies)
│ │ ├── user_repository.py
│ │ └── policy_repository.py
│ ├── models/ # Domain models for users and policies
│ │ ├── user.py
│ │ └── policy.py
│ └── config/ # Configuration for MCP server
│ └── settings.py
├── tests/ # Unit tests for services and repositories
├── Dockerfile # Container image definition
├── pyproject.toml # Python project dependencies
└── .env.example # Environment variable template

---

## Key Concepts

### 1. Repositories
- Responsible for fetching raw data from storage (CSV, JSON, DB).
- Do **not** contain business logic.
- Examples: `get_user_by_id()`, `get_current_policy()`

### 2. Models
- Convert raw data into **typed, validated objects**.
- Ensure services always receive correct data.
- Examples: `User`, `CashISAPolicy`

### 3. Services
- Contain the **business logic** (eligibility, allowance calculations, policy rules).
- Do **not** fetch data or communicate with agents.
- Examples: `is_user_eligible()`, `remaining_allowance()`, `can_open_new_isa()`

### 4. Tools
- **Bridge between services and agents**.
- Accept raw inputs (e.g., user_id), fetch data via repositories, convert to models, call services, return structured output.
- Examples: `check_user_eligibility()`, `check_can_open_new_isa()`

---

## Example Usage

```python
from src.tools.eligibility_tools import check_user_eligibility

result = check_user_eligibility("u123")
print(result)
# Output:
# {
#   "user_id": "u123",
#   "eligible": True,
#   "remaining_allowance": 16500.0
# }
