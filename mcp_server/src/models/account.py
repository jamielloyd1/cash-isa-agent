from dataclasses import dataclass
from datetime import date

@dataclass
class Account:
    """
    Represents a bank account (Cash ISA, Stocks ISA, Lifetime ISA, or Current Account).
    
    These fields come directly from accounts.csv
    """
    
    account_number: int             # Unique identifier for this account (e.g., 1001)
    user_id: str                    # Who owns this account? (e.g., "USR001")
    account_type: str               # Type of account: "Cash ISA", "Stocks and Shares ISA", "Lifetime ISA", "Innovative Finance ISA", or "Current Account"
    account_balance: float          # How much money is in it right now (e.g., 21500.00)
    opened_date: date                # When was it opened? (e.g., "2023-06-15")
    
    def __str__(self):
        return f"Account({self.account_number}: {self.account_type}, balance £{self.account_balance})"
    
    def is_cash_isa(self) -> bool:
        """Is this a Cash ISA?"""
        return self.account_type == "Cash ISA"
    
    def is_isa(self) -> bool:
        """Is this any type of ISA? (excludes Current Account)"""
        isa_types = ["Cash ISA", "Stocks and Shares ISA", "Lifetime ISA", "Innovative Finance ISA"]
        return self.account_type in isa_types
    
    def opened_in_current_tax_year(self, tax_year_start: date) -> bool:
        """
        Was this account opened in the current tax year?
        
        tax_year_start should be "2025-06-04"
        Returns True if opened_date is on or after that date
        
        Example:
          - "2025-07-10" >= "2025-06-04" → True (opened in current tax year)
          - "2025-05-01" >= "2025-06-04" → False (opened in previous tax year)
        """
        return self.opened_date >= tax_year_start
    

