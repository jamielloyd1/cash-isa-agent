from pathlib import Path
import csv
from typing import List, Optional
from datetime import datetime
from models import Account
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from src/repositories
sys.path.insert(0, str(PROJECT_ROOT))

from config import USERS_CSV, ACCOUNTS_CSV, TRANSACTIONS_CSV


class AccountRepository:
    """
    Loads accounts from accounts.csv and provides methods to fetch account objects.
    """

    def __init__(self, csv_path: Optional[str] = None):
        # Use config path if none provided
        if csv_path is None:
            self.csv_path = ACCOUNTS_CSV
        else:
            self.csv_path = Path(csv_path).resolve()

    def get_all_accounts(self) -> List[Account]:
        accounts = []
        with self.csv_path.open(newline="", encoding="utf-8") as csvfile:
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
        with self.csv_path.open(newline="", encoding="utf-8") as csvfile:
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
        with self.csv_path.open(newline="", encoding="utf-8") as csvfile:
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
    

    def save_account(self, account: Account):
        """Append a new account to the CSV file."""
        fieldnames = ["account_number", "user_id", "account_type", "account_balance", "opened_date"]
        file_exists = self.csv_path.exists()
        with self.csv_path.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "account_number": account.account_number,
                "user_id": account.user_id,
                "account_type": account.account_type,
                "account_balance": account.account_balance,
                "opened_date": account.opened_date.isoformat()
            })

    def update_account_balance(self, account_number: int, amount: float):
        """Update account balance by adding 'amount' to the existing balance."""
        accounts = self.get_all_accounts()
        updated_rows = []

        for acc in accounts:
            if acc.account_number == account_number:
                acc.account_balance += amount
            updated_rows.append(acc)

        # Write all accounts back to CSV
        fieldnames = ["account_number", "user_id", "account_type", "account_balance", "opened_date"]
        with self.csv_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for acc in updated_rows:
                writer.writerow({
                    "account_number": acc.account_number,
                    "user_id": acc.user_id,
                    "account_type": acc.account_type,
                    "account_balance": acc.account_balance,
                    "opened_date": acc.opened_date.isoformat()
                })



    def update_account_balance(self, account_number: int, amount: float):
        """Update account balance by adding 'amount' to the existing balance."""
        accounts = self.get_all_accounts()
        updated_rows = []

        for acc in accounts:
            if acc.account_number == account_number:
                acc.account_balance += amount
            updated_rows.append(acc)

        # Write all accounts back to CSV
        fieldnames = ["account_number", "user_id", "account_type", "account_balance", "opened_date"]
        with self.csv_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for acc in updated_rows:
                writer.writerow({
                    "account_number": acc.account_number,
                    "user_id": acc.user_id,
                    "account_type": acc.account_type,
                    "account_balance": acc.account_balance,
                    "opened_date": acc.opened_date.isoformat()
                })