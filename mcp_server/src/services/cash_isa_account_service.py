from datetime import date
from pathlib import Path
from models import Account, Transaction
from datetime import date
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from src/repositories
sys.path.insert(0, str(PROJECT_ROOT))

from config import USERS_CSV, ACCOUNTS_CSV, TRANSACTIONS_CSV

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
        contribution_policy
    ):
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.eligibility_policy = eligibility_policy
        self.contribution_policy = contribution_policy

    # ------------------- Eligibility checks -------------------

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

        if not (user.uk_resident or user.crown_servant or user.crown_servant_spouse):
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

    # ------------------- Account operations -------------------

    def open_cash_isa(self, user_id: str, deposit: float) -> Account:
        """Creates a new Cash ISA account and initial transaction."""
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

        # Use repository to save the account
        self.account_repo.save_account(new_account)

        new_transaction = Transaction(
            transaction_id=self.generate_transaction_id(),
            account_number=new_account.account_number,
            user_id=user_id,
            amount=deposit,
            date=today_date,
            type="opening_deposit"
        )

        # Use repository to save the transaction
        self.transaction_repo.save_transaction(new_transaction)

        return new_account

    # ------------------- ID generation -------------------

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