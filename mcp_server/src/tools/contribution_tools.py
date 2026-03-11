
from typing import Dict, Any
from services.user_service import UserService
from services.cash_isa_account_service import CashISAAccountService
from services.cash_isa_contribution_service import CashISAContributionService




class ContributionTools:
    def __init__(self, user_service: UserService, cash_isa_account_service: CashISAAccountService, cash_isa_contribution_service: CashISAContributionService):
        self.user_service = user_service
        self.cash_isa_account_service = cash_isa_account_service
        self.cash_isa_contribution_service = cash_isa_contribution_service

    def check_contribution_eligibility(self, user_id: str, account_number: int | None = None) -> Dict[str, Any]:
        """Checks if the user can contribute to a Cash ISA account."""
        try:
            result = self.cash_isa_contribution_service.can_contribute_to_cash_isa(user_id, account_number)

            return {
                "success": True,
                "can_contribute": result.can_contribute,
                "reason": result.reason
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        

    def check_contribution_amount(self, user_id: str) -> Dict[str, Any]:
        """ checks how much the user can contribute to a Cash ISA account."""
        try:
            contribution_amount = self.cash_isa_contribution_service.contribution_amount_remaining_for_tax_year(user_id)
            remaining, eligible_accounts = contribution_amount


            if remaining == 0.0:
                return {
                    "success": True,
                    "can_contribute": False,
                    "reason": eligible_accounts[0] if eligible_accounts else "User has no remaining contribution allowance for this tax year."
                }

            return {
                "success": True,
                "can_contribute": remaining > 0,
                "contribution_amount": remaining,
                "eligible_accounts": eligible_accounts if eligible_accounts else None
            }

        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def contribute_to_cash_isa(self, user_id: str, account_number: int, amount: float) -> Dict[str, Any]:
        """Attempts to contribute to a Cash ISA account."""
        try:
            self.cash_isa_contribution_service.make_contribution(user_id, account_number, amount)

            return {
                "success": True,
                "message": f"Successfully contributed £{amount:.2f} to Cash ISA account {account_number}."
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }