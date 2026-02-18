from dataclasses import dataclass
from datetime import date

@dataclass
class CashISAEligibilityPolicy:
    """
    The rules that decide if someone can OPEN a Cash ISA.
    
    These come from data/policies/cash_isa/eligibility.json
    """
    
    minimum_age: int = 18
    require_uk_residency_or_crown_status: bool = True

    def __str__(self):
        return f"CashISAEligibilityPolicy(min_age={self.minimum_age}, require_uk_residency_or_crown_status={self.require_uk_residency_or_crown_status})"


@dataclass
class CashISAContributionPolicy:

    annual_limit_all_isas: float = 20000.00
    max_accounts_contributed_per_year: int = 1

    def __init__(self):
        today = date.today()

        if today >= date(today.year, 4, 6):
            self.tax_year_start = date(today.year, 4, 6)
            self.tax_year_end = date(today.year + 1, 4, 5)
        else:
            self.tax_year_start = date(today.year - 1, 4, 6)
            self.tax_year_end = date(today.year, 4, 5)

    def __str__(self):
        return (
            f"ContributionPolicy(limit=£{self.annual_limit_all_isas}, "
            f"one_per_year={self.max_accounts_contributed_per_year})"
        )