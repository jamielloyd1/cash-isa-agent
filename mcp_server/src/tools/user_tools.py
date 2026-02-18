
from typing import Dict, Any
from services.user_service import UserService
from services.cash_isa_account_service import CashISAAccountService



class UserTools:
    def __init__(self, user_service: UserService, cash_isa_account_service: CashISAAccountService):
        self.user_service = user_service
        self.cash_isa_account_service = cash_isa_account_service


    def get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Fetches user details for a given user ID."""
        try:
            user = self.user_service.get_user(user_id)

            if not user:
                return {
                    "success": False,
                    "error": "User not found."
                }

            return {
                "success": True,
                "user_id": user.user_id,
                "name": user.name,
                "age": user.age,
                "uk_resident": user.uk_resident,
                "crown_servant": user.crown_servant,
                "crown_servant_spouse": user.crown_servant_spouse,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
    def create_user(self, name: str, age: int, uk_resident: bool, crown_servant: bool, crown_servant_spouse: bool) -> Dict[str, Any]:
        """Creates a new user with the provided details."""
        try:
            new_user = self.user_service.create_user(name, age, uk_resident, crown_servant, crown_servant_spouse)

            return {
                "success": True,
                "user_id": new_user.user_id,
                "message": "User created successfully."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }