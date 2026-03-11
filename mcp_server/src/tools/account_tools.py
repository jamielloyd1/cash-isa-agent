# account_tools.py

from typing import Dict, Any
from services.user_service import UserService
from services.cash_isa_account_service import CashISAAccountService



class AccountTools:
    def __init__(self, user_service: UserService, cash_isa_account_service: CashISAAccountService):
        self.user_service = user_service
        self.cash_isa_account_service = cash_isa_account_service


    def get_all_account_details(self, user_id: str) -> Dict[str, Any]:
        """Fetches all account details for a given user."""
        try:
            accounts = self.user_service.get_accounts_for_user(user_id)

            return {
                "success": True,
                "accounts": [
                    {
                        "account_number": a.account_number,
                        "account_type": a.account_type,
                        "account_balance": a.account_balance,
                        "opened_date": a.opened_date,
                    }
                    for a in accounts
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


    def open_cash_isa(self, user_id: str, deposit: float) -> Dict[str, Any]:

        """Attempts to open a new Cash ISA for the user with the specified deposit amount."""
        try:
            account = self.cash_isa_account_service.open_cash_isa(user_id, deposit)

            return {
                "success": True,
                "account_number": account.account_number,
                "message": "Cash ISA opened successfully."
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }

        except Exception:
            return {
                "success": False,
                "error": "Unexpected error occurred while opening account."
            }
