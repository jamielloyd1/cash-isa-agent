import csv
from typing import List, Optional
from pathlib import Path
from models import User
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from src/repositories
sys.path.insert(0, str(PROJECT_ROOT))

from config import USERS_CSV, ACCOUNTS_CSV, TRANSACTIONS_CSV

class UserRepository:
    """
    Loads users from users.csv and provides methods to fetch user objects.
    """
    def __init__(self, csv_path: Path = USERS_CSV):
        self.csv_path = Path(csv_path)

    def get_all_users(self) -> List[User]:
        users = []
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user = User(
                    user_id=row['user_id'],
                    name=row['name'],
                    age=int(row['age']),
                    uk_resident=row['uk_resident'].lower() == 'true',
                    crown_servant=row['crown_servant'].lower() == 'true',
                    crown_servant_spouse=row['crown_servant_spouse'].lower() == 'true',
                )
                users.append(user)
        return users

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == user_id:
                    return User(
                        user_id=row['user_id'],
                        name=row['name'],
                        age=int(row['age']),
                        uk_resident=row['uk_resident'].lower() == 'true',
                        crown_servant=row['crown_servant'].lower() == 'true',
                        crown_servant_spouse=row['crown_servant_spouse'].lower() == 'true',
                    )
        return None
    

    def add_user(self, user: User):
        file_exists = self.csv_path.exists()

        with self.csv_path.open("a", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "user_id",
                "name",
                "age",
                "uk_resident",
                "crown_servant",
                "crown_servant_spouse",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                "user_id": user.user_id,
                "name": user.name,
                "age": user.age,
                "uk_resident": user.uk_resident,
                "crown_servant": user.crown_servant,
                "crown_servant_spouse": user.crown_servant_spouse,
            })
