import sys
from pathlib import Path

# Add the 'src' folder to Python's module search path
sys.path.append(str(Path(__file__).parent / "src"))
#print("sys.path:", sys.path)

from models.cash_isa_policy import CashISAEligibilityPolicy, CashISAContributionPolicy
from tools import register_tools

from repositories.user_repository import UserRepository
from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository

from services.user_service import UserService
from services.cash_isa_account_service import CashISAAccountService
from services.cash_isa_contribution_service import CashISAContributionService
from fastmcp import FastMCP


mcp = FastMCP("ISA account management server")


# Create repositories

user_repo = UserRepository()
account_repo = AccountRepository()
transaction_repo = TransactionRepository()

#Create Policies
eligibility_policy = CashISAEligibilityPolicy()
contribution_policy = CashISAContributionPolicy()


# Create services

user_service = UserService(user_repo)
cash_isa_account_service = CashISAAccountService(user_repo, account_repo, transaction_repo, eligibility_policy, contribution_policy)
cash_isa_contribution_service = CashISAContributionService(user_repo, account_repo, transaction_repo, eligibility_policy, contribution_policy)

# Bundle services for tool registration
services = {
    "user_service": user_service,
    "cash_isa_account_service": cash_isa_account_service,
    "cash_isa_contribution_service": cash_isa_contribution_service,
}


# Register all MCP tools

register_tools(mcp, services)


# Start server
if __name__ == "__main__":
    mcp.run()
