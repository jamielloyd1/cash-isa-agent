from models import Account, User, Transaction
from repositories import UserRepository, AccountRepository, TransactionRepository
from models import CashISAEligibilityPolicy, CashISAContributionPolicy
from datetime import date
import csv 
from dataclasses import dataclass
from typing import Optional
from .cash_isa_account_service import CashISAAccountService

@dataclass
class ContributionCheckResult:
    can_contribute: bool
    reason: Optional[str] = None


class CashISAContributionService:
    """
    This service contains the business logic for Cash ISA contributions.
    
    It uses the repositories to get data about users, accounts, transactions, and policies,
    and then applies the rules to determine if certain contribution actions are allowed.
    """
    
    def __init__(self, user_repo, account_repo, transaction_repo, eligibility_policy, contribution_policy, accounts_csv_path: str = '../../data/users/accounts.csv', transactions_csv_path: str = '../../data/users/transactions.csv'):
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.eligibility_policy = eligibility_policy
        self.contribution_policy = contribution_policy
        self.accounts_csv_path = accounts_csv_path
        self.transactions_csv_path = transactions_csv_path

    def can_contribute_to_cash_isa(
        self,
        user_id: str,
        account_number: str | None = None,
    ) -> ContributionCheckResult:

        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            return ContributionCheckResult(False, "User not found.")

        if not self._has_cash_isa(user):
            return ContributionCheckResult(False, "User does not have a Cash ISA account.")

        meets_rules, reason = self._meets_contribution_rules(
            user_id=user_id,
            account_number=account_number,
        )

        if not meets_rules:
            return ContributionCheckResult(False, reason)

        return ContributionCheckResult(True)


    
    def _has_cash_isa(self, user) -> bool:
        accounts = self.account_repo.get_accounts_by_user_id(user.user_id)
        has_cash_isa = any(account.account_type == 'cash_isa' for account in accounts)
        return has_cash_isa


    def _meets_contribution_rules(
        self,
        user_id: str,
        account_number: str | None = None,
    ) -> tuple[bool, str | None]:

        accounts = self.account_repo.get_accounts_by_user_id(user_id)

        isa_accounts = [
            account for account in accounts
            if account.account_type in [
                "cash_isa",
                "Lifetime ISA",
                "Stocks and Shares ISA",
                "Innovative Finance ISA",
            ]
        ]

        # ---- RULE 1: Annual ISA allowance ----
        total_contributions = 0

        for account in isa_accounts:
            transactions = self.transaction_repo.get_transactions_by_account_number(
                account.account_number
            )

            for transaction in transactions:
                if (
                    transaction.date >= self.contribution_policy.tax_year_start
                    and transaction.type in ["contribution", "opening-deposit"]
                ):
                    total_contributions += transaction.amount

        if total_contributions >= self.contribution_policy.annual_limit_all_isas:
            return False, "Annual ISA contribution limit has been reached."

        # ---- RULE 2: Contributed to another Cash ISA this tax year ----
        if account_number:
            valid, reason = self._has_contributed_to_different_cash_isa_this_year(
                user_id=user_id,
                current_account_number=account_number,
            )
            if not valid:
                return False, reason

        return True, None
    

    def _has_contributed_to_different_cash_isa_this_year(
        self,
        user_id: str,
        current_account_number: str,
    ) -> tuple[bool, str | None]:

        contributed_accounts = self._get_cash_isa_accounts_contributed_this_tax_year(
            user_id
        )

        # Remove the current account if present
        other_accounts = [
            acc for acc in contributed_accounts
            if acc != current_account_number
        ]

        if other_accounts:
            return (
                False,
                "User has already contributed to a different Cash ISA this tax year.",
            )

        return True, None




    def _get_cash_isa_accounts_contributed_this_tax_year(
        self,
        user_id: str,
    ) -> list[str]:

        accounts = self.account_repo.get_accounts_by_user_id(user_id)

        cash_isa_accounts = [
            account for account in accounts
            if account.account_type == "cash_isa"
        ]

        contributed_accounts = []

        for account in cash_isa_accounts:
            transactions = self.transaction_repo.get_transactions_by_account_number(
                account.account_number
            )

            for transaction in transactions:
                if (
                    transaction.date >= self.contribution_policy.tax_year_start
                    and transaction.type in ["contribution", "opening-deposit"]
                ):
                    contributed_accounts.append(account.account_number)
                    break  # No need to check more transactions for this account

        return contributed_accounts
    

    def contribution_amount_remaining_for_tax_year(
        self,
        user_id: str
    ) -> tuple[float, list[str]]:
        
        if not self.can_contribute_to_cash_isa(user_id).can_contribute:
            return 0.0, ["User is not eligible to contribute to a Cash ISA."]

        # Get all ISA accounts for the user
        accounts = self.account_repo.get_accounts_by_user_id(user_id)

        isa_accounts = [
            account for account in accounts
            if account.account_type in [
                "cash_isa",
                "Lifetime ISA",
                "Stocks and Shares ISA",
                "Innovative Finance ISA",
            ]
        ]

        # Calculate total contributions this tax year
        total_contributions = 0
        for account in isa_accounts:
            transactions = self.transaction_repo.get_transactions_by_account_number(
                account.account_number
            )
            for transaction in transactions:
                if (
                    transaction.date >= self.contribution_policy.tax_year_start
                    and transaction.type in ["contribution", "opening-deposit"]
                ):
                    total_contributions += transaction.amount

        remaining = max(self.contribution_policy.annual_limit_all_isas - total_contributions, 0)

        # Determine eligible accounts
        contributed_cash_isas = self._get_cash_isa_accounts_contributed_this_tax_year(user_id)

        if contributed_cash_isas:
            eligible_accounts = contributed_cash_isas
        else:
            # No contributions yet: all cash ISA accounts are eligible
            eligible_accounts = [
                account.account_number for account in accounts if account.account_type == "cash_isa"
            ]

        return remaining, eligible_accounts
    
    def make_contribution(self, user_id: str, account_number: str, amount: float) -> bool:
        # This method would contain the logic to actually record a contribution transaction,
        # update the account balance, and ensure all rules are still met after the contribution.
        # For now, we can just return True to indicate success.
        if not self.can_contribute_to_cash_isa(user_id).can_contribute:
            raise ValueError("User is not eligible to contribute to a Cash ISA.")
        if amount <= 0:
            raise ValueError("Contribution amount must be positive.")
        
        if amount > self.contribution_amount_remaining_for_tax_year(user_id)[0]:
            raise ValueError("Contribution amount exceeds remaining allowance for this tax year.")
        
        if account_number not in self.contribution_amount_remaining_for_tax_year(user_id)[1]:
            raise ValueError("This account is not eligible for contributions this tax year.")
        
                
        account_service = CashISAAccountService(self.user_repo, self.account_repo, self.transaction_repo, self.eligibility_policy, self.contribution_policy)
        new_transaction = Transaction(
            transaction_id=CashISAAccountService.generate_transaction_id(account_service),
            account_number=account_number,
            user_id=user_id,
            amount=amount,
            date=date.today(),
            type="contribution"
        )

        # Save transaction to CSV
        account_service.save_transaction(new_transaction)

        # Update account balance in CSV
        account_service._update_account_balance(account_number, amount)
        

        return True
    