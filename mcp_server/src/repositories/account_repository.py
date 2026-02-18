import csv
from typing import List, Optional
from pathlib import Path
from models import Account
from datetime import datetime


class AccountRepository:
    """
    Loads accounts from accounts.csv and provides methods to fetch account objects.
    """
    def __init__(self, csv_path: str = '../../data/users/accounts.csv'):

        self.csv_path = Path(csv_path)

    def get_all_accounts(self) -> List[Account]:
        accounts = []
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                account = Account(
                    account_number=int(row['account_number']),
                    user_id=row['user_id'],
                    account_type=row['account_type'],
                    account_balance=float(row['account_balance']),
                    opened_date=datetime.strptime(row['opened_date'], '%Y-%m-%d').date()
                )
                accounts.append(account)
        return accounts
    

    def get_account_by_number(self, account_number: int) -> Optional[Account]:
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['account_number']) == account_number:
                    return Account(
                        account_number=int(row['account_number']),
                        user_id=row['user_id'],
                        account_type=row['account_type'],
                        account_balance=float(row['account_balance']),
                        opened_date=datetime.strptime(row['opened_date'], '%Y-%m-%d').date()
                    )
        return None
                    

    def get_accounts_by_user_id(self, user_id: str) -> List[Account]:
        accounts = []
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == user_id:
                    account = Account(
                        account_number=int(row['account_number']),
                        user_id=row['user_id'],
                        account_type=row['account_type'],
                        account_balance=float(row['account_balance']),
                        opened_date=datetime.strptime(row['opened_date'], '%Y-%m-%d').date()
                    )
                    accounts.append(account)
        return accounts