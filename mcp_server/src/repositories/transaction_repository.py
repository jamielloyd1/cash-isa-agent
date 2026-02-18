import csv
from typing import List, Optional
from pathlib import Path
from models import Transaction
from datetime import datetime


class TransactionRepository:
    """
    Loads transactions from transactions.csv and provides methods to fetch transaction objects.
    """
    def __init__(self, csv_path: str = '../../data/users/transactions.csv'):

        self.csv_path = Path(csv_path)
    

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['transaction_id']) == transaction_id:
                    return Transaction(
                        transaction_id=row['transaction_id'],
                        account_number=int(row['account_number']),
                        user_id=row['user_id'],
                        amount=float(row['amount']),
                        date=datetime.strptime(row['date'],"%Y-%m-%d").date(),
                        type=row['type']
                    )
        return None
                    

    def get_transactions_by_account_number(self, account_number: int) -> List[Transaction]:
        transactions = []
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['account_number']) == account_number:
                    transaction = Transaction(
                        transaction_id=row['transaction_id'],
                        account_number=int(row['account_number']),
                        user_id=row['user_id'],
                        amount=float(row['amount']),
                        date=datetime.strptime(row['date'],"%Y-%m-%d").date(),
                        type=row['type']
                    )
                    transactions.append(transaction)
        return transactions


    def get_transactions_by_user_id(self, user_id: str) -> List[Transaction]:
        transactions = []
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == user_id:
                    transaction = Transaction(
                        transaction_id=row['transaction_id'],
                        account_number=int(row['account_number']),
                        user_id=row['user_id'],
                        amount=float(row['amount']),
                        date=datetime.strptime(row['date'],"%Y-%m-%d").date(),
                        type=row['type']
                    )
                    transactions.append(transaction)
        return transactions
     