from typing import Optional
from models import User
from repositories import UserRepository, AccountRepository
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from src/repositories
sys.path.insert(0, str(PROJECT_ROOT))

from config import USERS_CSV, ACCOUNTS_CSV, TRANSACTIONS_CSV


class UserService:
    """
    Service layer for user-related operations.
    Business logic is here; data storage is delegated to UserRepository.
    """

    def __init__(self, user_repository: UserRepository = None, account_repository: AccountRepository = None):
        # Use the repository; default to USERS_CSV from config
        self.user_repository = user_repository or UserRepository(csv_path=USERS_CSV)
        self.account_repository = account_repository or AccountRepository(csv_path=ACCOUNTS_CSV)

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repository.get_user_by_id(user_id)
    

    def get_accounts_for_user(self, user_id: str) -> list:
        """Return all accounts for a given user."""
        return self.account_repository.get_accounts_by_user_id(user_id)

    def get_all_users(self) -> list[User]:
        """Return all users."""
        return self.user_repository.get_all_users()

    def create_user(
        self,
        name: str,
        age: int,
        uk_resident: bool,
        crown_servant: bool,
        crown_servant_spouse: bool
    ) -> User:
        """
        Create a new User object with a unique ID and save it via the repository.
        """

        # Generate a new unique user_id
        all_users = self.user_repository.get_all_users()
        if not all_users:
            user_id = "USR001"
        else:
            last_id = sorted([int(u.user_id[3:]) for u in all_users])[-1]
            user_id = f"USR{last_id + 1:03d}"

        # Create User object
        new_user = User(
            user_id=user_id,
            name=name,
            age=age,
            uk_resident=uk_resident,
            crown_servant=crown_servant,
            crown_servant_spouse=crown_servant_spouse
        )

        # Persist user via repository
        self.user_repository.add_user(new_user)

        return new_user