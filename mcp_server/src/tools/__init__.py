from .user_tools import UserTools
from .account_tools import AccountTools
from .contribution_tools import ContributionTools
from .eligibility_tools import EligibilityTools

from services.user_service import UserService
from services.cash_isa_account_service import CashISAAccountService
from services.cash_isa_contribution_service import CashISAContributionService

def register_tools(mcp, services):
    """
    Registers all MCP tools.

    Args:
        mcp: MCP server instance
        services: dict containing service instances
    """

    user_tools = UserTools(services["user_service"], services["cash_isa_account_service"])
    account_tools = AccountTools(services["user_service"], services["cash_isa_account_service"])
    contribution_tools = ContributionTools(services["user_service"], services["cash_isa_account_service"], services["cash_isa_contribution_service"])
    eligibility_tools = EligibilityTools(services["user_service"], services["cash_isa_account_service"])


    # User tools
    mcp.tool()(user_tools.get_user_details)
    mcp.tool()(user_tools.create_user)
    
    # Account tools
    mcp.tool()(account_tools.get_all_account_details)
    mcp.tool()(account_tools.open_cash_isa)

    # Contribution tools
    mcp.tool()(contribution_tools.check_contribution_eligibility)
    mcp.tool()(contribution_tools.check_contribution_amount)
    mcp.tool()(contribution_tools.contribute_to_cash_isa)

    # Eligibility tools
    mcp.tool()(eligibility_tools.check_cash_isa_eligibility)
