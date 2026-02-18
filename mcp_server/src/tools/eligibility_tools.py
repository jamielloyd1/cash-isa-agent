
from typing import Dict, Any
from services.user_service import UserService
from services.cash_isa_account_service import CashISAAccountService



class EligibilityTools:
    def __init__(self, user_service: UserService, cash_isa_account_service: CashISAAccountService):
        self.user_service = user_service
        self.cash_isa_account_service = cash_isa_account_service


    def check_cash_isa_eligibility(self, user_id: str) -> Dict[str, Any]:
        """Checks if the user is eligible to open a Cash ISA account."""
        try:
            can_open = self.cash_isa_account_service.can_open_cash_isa(user_id)

            if can_open:
                return {
                    "success": True,
                    "eligible": True,
                    "message": "User is eligible to open a Cash ISA account."
                }
            else:
                return {
                    "success": True,
                    "eligible": False,
                    "message": "User is not eligible to open a Cash ISA account."
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }