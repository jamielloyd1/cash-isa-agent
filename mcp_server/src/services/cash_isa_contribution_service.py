from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Tuple
import csv

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from src/repositories
sys.path.insert(0, str(PROJECT_ROOT))

from config import USERS_CSV, ACCOUNTS_CSV, TRANSACTIONS_CSV
from models import Account, Transaction, CashISAEligibilityPolicy, CashISAContributionPolicy
from repositories import UserRepository, AccountRepository, TransactionRepository
from .cash_isa_account_service import CashISAAccountService



@dataclass
class ContributionCheckResult:
    can_contribute: bool
    reason: Optional[str] = None


class CashISAContributionService:
    def __init__(
        self,
        user_repo,
        account_repo,
        transaction_repo,
        eligibility_policy,
        contribution_policy,
    ):
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.eligibility_policy = eligibility_policy
        self.contribution_policy = contribution_policy

        # Account service to handle transactions and balance updates
        self.account_service = CashISAAccountService(
            self.user_repo,
            self.account_repo,
            self.transaction_repo,
            self.eligibility_policy,
            self.contribution_policy
        )

    def can_contribute_to_cash_isa(
        self, user_id: str, account_number: str | None = None
    ) -> ContributionCheckResult:

        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            return ContributionCheckResult(False, "User not found.")

        if not self._has_cash_isa(user):
            return ContributionCheckResult(False, "User does not have a Cash ISA account.")

        meets_rules, reason = self._meets_contribution_rules(user_id, account_number)

        if not meets_rules:
            return ContributionCheckResult(False, reason)

        return ContributionCheckResult(True)

    def _has_cash_isa(self, user) -> bool:
        accounts = self.account_repo.get_accounts_by_user_id(user.user_id)
        # standardize account_type check
        return any(account.account_type.lower().replace(" ", "_") == "cash_isa" for account in accounts)

    def _meets_contribution_rules(
        self, user_id: str, account_number: str | None = None
    ) -> Tuple[bool, Optional[str]]:

        accounts = self.account_repo.get_accounts_by_user_id(user_id)
        isa_accounts = [
            acc for acc in accounts
            if acc.account_type.lower().replace(" ", "_") in [
                "cash_isa", "lifetime_isa", "stocks_and_shares_isa", "innovative_finance_isa"
            ]
        ]

        total_contributions = 0
        for account in isa_accounts:
            transactions = self.transaction_repo.get_transactions_by_account_number(account.account_number)
            for txn in transactions:
                if txn.date >= self.contribution_policy.tax_year_start and txn.type in ["contribution", "opening-deposit"]:
                    total_contributions += txn.amount

        if total_contributions >= self.contribution_policy.annual_limit_all_isas:
            return False, "Annual ISA contribution limit has been reached."

        if account_number:
            valid, reason = self._has_contributed_to_different_cash_isa_this_year(user_id, account_number)
            if not valid:
                return False, reason

        return True, None

    def _has_contributed_to_different_cash_isa_this_year(
        self, user_id: str, current_account_number: str
    ) -> Tuple[bool, Optional[str]]:

        contributed_accounts = self._get_cash_isa_accounts_contributed_this_tax_year(user_id)
        other_accounts = [acc for acc in contributed_accounts if acc != current_account_number]

        if other_accounts:
            return False, "User has already contributed to a different Cash ISA this tax year."

        return True, None

    def _get_cash_isa_accounts_contributed_this_tax_year(self, user_id: str) -> List[str]:
        accounts = self.account_repo.get_accounts_by_user_id(user_id)
        cash_isa_accounts = [
            acc for acc in accounts if acc.account_type.lower().replace(" ", "_") == "cash_isa"
        ]

        contributed_accounts = []
        for account in cash_isa_accounts:
            transactions = self.transaction_repo.get_transactions_by_account_number(account.account_number)
            for txn in transactions:
                if txn.date >= self.contribution_policy.tax_year_start and txn.type in ["contribution", "opening-deposit"]:
                    contributed_accounts.append(account.account_number)
                    break

        return contributed_accounts

    def contribution_amount_remaining_for_tax_year(self, user_id: str) -> Tuple[float, List[str]]:
        if not self.can_contribute_to_cash_isa(user_id).can_contribute:
            return 0.0, ["User is not eligible to contribute to a Cash ISA."]

        accounts = self.account_repo.get_accounts_by_user_id(user_id)
        isa_accounts = [
            acc for acc in accounts
            if acc.account_type.lower().replace(" ", "_") in ["cash_isa", "lifetime_isa", "stocks_and_shares_isa", "innovative_finance_isa"]
        ]

        total_contributions = 0
        for account in isa_accounts:
            transactions = self.transaction_repo.get_transactions_by_account_number(account.account_number)
            for txn in transactions:
                if txn.date >= self.contribution_policy.tax_year_start and txn.type in ["contribution", "opening-deposit"]:
                    total_contributions += txn.amount

        remaining = max(self.contribution_policy.annual_limit_all_isas - total_contributions, 0)

        contributed_cash_isas = self._get_cash_isa_accounts_contributed_this_tax_year(user_id)
        eligible_accounts = contributed_cash_isas if contributed_cash_isas else [
            acc.account_number for acc in accounts if acc.account_type.lower().replace(" ", "_") == "cash_isa"
        ]

        return remaining, eligible_accounts

    def make_contribution(self, user_id: str, account_number: str, amount: float) -> bool:
        check = self.can_contribute_to_cash_isa(user_id)
        if not check.can_contribute:
            raise ValueError(check.reason or "User cannot contribute.")
        if amount <= 0:
            raise ValueError("Contribution amount must be positive.")

        remaining, eligible_accounts = self.contribution_amount_remaining_for_tax_year(user_id)
        if amount > remaining:
            raise ValueError("Contribution amount exceeds remaining allowance")
        if account_number not in eligible_accounts:
            raise ValueError("This account is not eligible for contributions this tax year.")

        new_transaction = Transaction(
            transaction_id=self.account_service.generate_transaction_id(),
            account_number=account_number,
            user_id=user_id,
            amount=amount,
            date=date.today(),
            type="contribution"
        )

        self.account_service.transaction_repo.save_transaction(new_transaction)
        self.account_service.account_repo.update_account_balance(account_number, amount)

        return True