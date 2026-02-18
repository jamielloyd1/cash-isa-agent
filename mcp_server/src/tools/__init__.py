from .account_tools import AccountTools
from .contribution_tools import ContributionTools
from .eligibility_tools import EligibilityTools


def register_tools(mcp, services):
    """
    Registers all MCP tools.

    Args:
        mcp: MCP server instance
        services: dict containing service instances
    """

    account_tools = AccountTools(services["account_service"])
    contribution_tools = ContributionTools(services["contribution_service"])
    eligibility_tools = EligibilityTools(services["eligibility_service"])

    # Account tools
    mcp.tool()(account_tools.get_all_account_details)
    mcp.tool()(account_tools.open_cash_isa)

    # Contribution tools
    mcp.tool()(contribution_tools.check_contribution_eligibility)
    mcp.tool()(contribution_tools.check_contribution_amount)
    mcp.tool()(contribution_tools.contribute_to_cash_isa)

    # Eligibility tools
    mcp.tool()(eligibility_tools.check_cash_isa_eligibility)
