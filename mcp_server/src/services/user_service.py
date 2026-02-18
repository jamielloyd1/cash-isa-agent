from typing import Optional 
from repositories import UserRepository 
from models import User
import csv


class UserService:
    """
    Service layer for user-related operations.
    """
    def __init__(self, user_repository: UserRepository, csv_path: str = '../../data/users/users.csv'): 
        self.user_repository = user_repository
        self.csv_path = csv_path

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repository.get_user_by_id(user_id)
    

    def get_all_users(self):
        """Return a list of all User objects."""
        return self.user_repository.get_all_users()
    

    def get_accounts_for_user(self, user_id: str):
        user = self.get_user(user_id)
        if not user:
            return None
        return self.account_repository.get_accounts_by_user_id(user_id)


    def create_user(self, name: str, age: int, uk_resident: bool, crown_servant: bool, crown_servant_spouse: bool) -> User:
        #Generate a new user ID
        user_id = self._generate_user_id()

        #Create the User object
        new_user = User(
            user_id=user_id,
            name=name,
            age=age,
            uk_resident=uk_resident,
            crown_servant=crown_servant,
            crown_servant_spouse=crown_servant_spouse
        )

        #Append to CSV
        file_exists = self.csv_path.exists()
        with self.csv_path.open("a", newline="", encoding="utf-8") as csvfile:
            fieldnames = ['user_id', 'name', 'age', 'uk_resident', 'crown_servant', 'crown_servant_spouse']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerow({
                'user_id': new_user.user_id,
                'name': new_user.name,
                'age': new_user.age,
                'uk_resident': new_user.uk_resident,
                'crown_servant': new_user.crown_servant,
                'crown_servant_spouse': new_user.crown_servant_spouse
            })

        #Return the created user
        return new_user
    

    def _generate_user_id(self) -> str:
        """Generate a new unique user ID like USR001, USR002, etc."""
        users = self.get_all_users()
        if not users:
            return "USR001"
        last_id = sorted([int(u.user_id[3:]) for u in users])[-1]
        return f"USR{last_id + 1:03d}"
    
