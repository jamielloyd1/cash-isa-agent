from models import Account, Transaction
from datetime import date
from pathlib import Path
import csv


class CashISAAccountService:
    """
    This service contains the business logic for Cash ISAs.
    
    It uses the repositories to get data about users, accounts, transactions, and policies,
    and then applies the rules to determine if certain actions are allowed.
    """

    def __init__(
        self,
        user_repo,
        account_repo,
        transaction_repo,
        eligibility_policy,
        contribution_policy,
        accounts_csv_path: str = '../../data/users/accounts.csv',
        transactions_csv_path: str = '../../data/users/transactions.csv'
    ):
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.eligibility_policy = eligibility_policy
        self.contribution_policy = contribution_policy
        self.accounts_csv_path = Path(accounts_csv_path)
        self.transactions_csv_path = Path(transactions_csv_path)

    def can_open_cash_isa(self, user_id: str) -> bool:
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            return False

        if not self._meets_eligibility_requirements(user):
            return False

        if not self._meets_tax_year_opening_rules(user_id):
            return False

        return True

    def _meets_eligibility_requirements(self, user) -> bool:
        if user.age < self.eligibility_policy.minimum_age:
            return False

        if not (
            user.uk_resident or
            user.crown_servant or
            user.crown_servant_spouse
        ):
            return False

        return True

    def _meets_tax_year_opening_rules(self, user_id: str) -> bool:
        accounts = self.account_repo.get_accounts_by_user_id(user_id)

        # Rule 1: Already opened a Cash ISA this tax year?
        for account in accounts:
            if account.account_type == "Cash ISA" and self._opened_this_tax_year(account):
                return False

        # Rule 2: Already contributed to a Cash ISA this tax year?
        if self._has_contributed_to_cash_isa_this_tax_year(user_id):
            return False

        # Rule 3: Already contributed £20,000 to any ISAs this tax year?
        if self._has_contributed_20k_to_isas_this_tax_year(user_id):
            return False

        return True

    def _opened_this_tax_year(self, account) -> bool:
        return self.contribution_policy.tax_year_start <= account.opened_date <= self.contribution_policy.tax_year_end

    def _has_contributed_to_cash_isa_this_tax_year(self, user_id: str) -> bool:
        transactions = self.transaction_repo.get_transactions_by_user_id(user_id)
        for txn in transactions:
            # Fetch account type from repository
            account = self.account_repo.get_account_by_number(txn.account_number)
            if account and account.account_type == "Cash ISA" and self._is_within_tax_year(txn.date):
                return True
        return False

    def _has_contributed_20k_to_isas_this_tax_year(self, user_id: str) -> bool:
        transactions = self.transaction_repo.get_transactions_by_user_id(user_id)
        total = 0.0
        for txn in transactions:
            account = self.account_repo.get_account_by_number(txn.account_number)
            if account and account.account_type in ["Cash ISA", "Lifetime ISA", "Stocks and Shares ISA", "Innovative Finance ISA"] and self._is_within_tax_year(txn.date):
                total += txn.amount
        return total >= 20000.0

    def _is_within_tax_year(self, check_date: date) -> bool:
        return self.contribution_policy.tax_year_start <= check_date <= self.contribution_policy.tax_year_end

    def open_cash_isa(self, user_id: str, deposit: float) -> Account:
        if not self.can_open_cash_isa(user_id):
            raise ValueError("User not eligible to open Cash ISA")

        if deposit < 0:
            raise ValueError("Deposit amount must be positive")

        today_date = date.today()

        new_account = Account(
            account_number=self._generate_account_number(),
            user_id=user_id,
            account_type="Cash ISA",
            account_balance=deposit,
            opened_date=today_date
        )

        # Save account to CSV
        self.account_repo.save_account(new_account)

        new_transaction = Transaction(
            transaction_id=self.generate_transaction_id(),
            account_number=new_account.account_number,
            user_id=user_id,
            amount=deposit,
            date=today_date,
            type="opening_deposit"
        )

        # Save transaction to CSV
        self.transaction_repo.save_transaction(new_transaction)

        return new_account

    def _generate_account_number(self) -> int:
        accounts = self.account_repo.get_all_accounts()
        if not accounts:
            return 1000
        return max(a.account_number for a in accounts) + 1

    def generate_transaction_id(self) -> str:
        transactions = self.transaction_repo.get_all_transactions()
        if not transactions:
            return "TXN0001"
        max_id = max(int(txn.transaction_id[3:]) for txn in transactions)
        return f"TXN{max_id + 1:04d}"




    def save_account(self, account: Account):
        """
        Append a new account to the accounts CSV file.
        """
        fieldnames = ["account_number", "user_id", "account_type", "account_balance", "opened_date"]

        # Ensure the file exists and write header if empty
        file_exists = self.accounts_csv_path.exists()
        with self.accounts_csv_path.open("a", newline="", encoding="utf-8") as csvfile:
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


    def save_transaction(self, transaction: Transaction):
        """
        Append a new transaction to the transactions CSV file.
        """
        fieldnames = ["transaction_id", "account_number", "user_id", "amount", "date", "type"]

        file_exists = self.transactions_csv_path.exists()
        with self.transactions_csv_path.open("a", newline="", encoding="utf-8") as csvfile:
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


    def _update_account_balance(self, account_number: int, amount: float):
        """
        Update the account_balance for a specific account in the CSV file.
        """
        if not self.accounts_csv_path.exists():
            raise FileNotFoundError(f"Accounts CSV file not found at {self.accounts_csv_path}")

        updated_rows = []

        # Read all rows and update the balance
        with self.accounts_csv_path.open("r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row["account_number"]) == account_number:
                    row["account_balance"] = str(float(row.get("account_balance", 0)) + amount)
                updated_rows.append(row)

        # Write back all rows
        fieldnames = updated_rows[0].keys() if updated_rows else ["account_number", "user_id", "account_type", "account_balance", "opened_date"]
        with self.accounts_csv_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

