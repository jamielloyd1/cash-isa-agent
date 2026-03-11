from pathlib import Path
import csv
from typing import List, Optional
from datetime import datetime
from models import Transaction
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from src/repositories
sys.path.insert(0, str(PROJECT_ROOT))

from config import USERS_CSV, ACCOUNTS_CSV, TRANSACTIONS_CSV


class TransactionRepository:
    """
    Loads transactions from transactions.csv and provides methods to fetch transaction objects.
    """

    def __init__(self, csv_path: Optional[str] = None):
        # Use config path if none provided
        if csv_path is None:
            self.csv_path = TRANSACTIONS_CSV
        else:
            self.csv_path = Path(csv_path).resolve()

    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        with self.csv_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['transaction_id'] == transaction_id:
                    return Transaction(
                        transaction_id=row['transaction_id'],
                        account_number=int(row['account_number']),
                        user_id=row['user_id'],
                        amount=float(row['amount']),
                        date=datetime.strptime(row['date'], "%Y-%m-%d").date(),
                        type=row['type']
                    )
        return None

    def get_transactions_by_account_number(self, account_number: int) -> List[Transaction]:
        transactions = []
        with self.csv_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['account_number']) == account_number:
                    transaction = Transaction(
                        transaction_id=row['transaction_id'],
                        account_number=int(row['account_number']),
                        user_id=row['user_id'],
                        amount=float(row['amount']),
                        date=datetime.strptime(row['date'], "%Y-%m-%d").date(),
                        type=row['type']
                    )
                    transactions.append(transaction)
        return transactions

    def get_transactions_by_user_id(self, user_id: str) -> List[Transaction]:
        transactions = []
        with self.csv_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == user_id:
                    transaction = Transaction(
                        transaction_id=row['transaction_id'],
                        account_number=int(row['account_number']),
                        user_id=row['user_id'],
                        amount=float(row['amount']),
                        date=datetime.strptime(row['date'], "%Y-%m-%d").date(),
                        type=row['type']
                    )
                    transactions.append(transaction)
        return transactions
    
    def save_transaction(self, transaction: Transaction):
        """Append a new transaction to the CSV file."""
        fieldnames = ["transaction_id", "account_number", "user_id", "amount", "date", "type"]
        file_exists = self.csv_path.exists()
        with self.csv_path.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "transaction_id": transaction.transaction_id,
                "account_number": transaction.account_number,
                "user_id": transaction.user_id,
                "amount": transaction.amount,
                "date": transaction.date.isoformat(),
                "type": transaction.type
            })


    def get_all_transactions(self) -> List[Transaction]:
        transactions = []
        with self.csv_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                transaction = Transaction(
                    transaction_id=row['transaction_id'],
                    account_number=int(row['account_number']),
                    user_id=row['user_id'],
                    amount=float(row['amount']),
                    date=datetime.strptime(row['date'], "%Y-%m-%d").date(),
                    type=row['type']
                )
                transactions.append(transaction)
        return transactions