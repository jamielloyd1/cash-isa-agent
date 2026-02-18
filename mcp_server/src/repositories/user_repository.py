import csv
from typing import List, Optional
from pathlib import Path
from models import User

class UserRepository:
    """
    Loads users from users.csv and provides methods to fetch user objects.
    """
    def __init__(self, csv_path: str = '../../data/users/users.csv'):
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
