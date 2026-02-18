from dataclasses import dataclass
from datetime import date

@dataclass
class Transaction:
    """
    Represents money going into or out of an account.
    
    These fields come directly from transactions.csv
    """
    
    transaction_id: str             # Unique identifier (e.g., "TXN002")
    account_number: int             # Which account is this for? (e.g., 1001)
    user_id: str                    # Who does it belong to? (e.g., "USR001")
    amount: float                   # How much money? (e.g., 6000.00)
    date: date                       # When did it happen? (e.g., "2025-07-10")
    type: str                       # What kind? "opening_deposit" or "contribution"
    
    def __str__(self):
        return f"Transaction({self.transaction_id}: £{self.amount} on {self.date})"
    
    def is_contribution(self) -> bool:
        """Is this a contribution (not an opening deposit)?"""
        return self.type == "contribution"
    
    def is_opening_deposit(self) -> bool:
        """Is this an opening deposit?"""
        return self.type == "opening_deposit"
