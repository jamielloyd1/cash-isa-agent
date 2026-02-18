import sys
from pathlib import Path
import pytest
from datetime import date

# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))
from models.account import Account

def test_account_str():
    acc = Account(account_number=1001, user_id="USR001", account_type="Cash ISA", account_balance=5000.0, opened_date=date(2025, 6, 15))
    expected_str = "Account(1001: Cash ISA, balance £5000.0)"
    assert str(acc) == expected_str

def test_is_cash_isa():
    acc_cash = Account(account_number=1002, user_id="USR002", account_type="Cash ISA", account_balance=2000.0, opened_date=date(2025, 6, 15))
    acc_current = Account(account_number=1003, user_id="USR003", account_type="Current Account", account_balance=3000.0, opened_date=date(2025, 6, 15))
    
    assert acc_cash.is_cash_isa() is True
    assert acc_current.is_cash_isa() is False

def test_is_isa():
    acc_cash = Account(account_number=1004, user_id="USR004", account_type="Cash ISA", account_balance=1000.0, opened_date=date(2025, 6, 15))
    acc_stocks = Account(account_number=1005, user_id="USR005", account_type="Stocks and Shares ISA", account_balance=5000.0, opened_date=date(2025, 6, 15))
    acc_current = Account(account_number=1006, user_id="USR006", account_type="Current Account", account_balance=7000.0, opened_date=date(2025, 6, 15))
    
    assert acc_cash.is_isa() is True
    assert acc_stocks.is_isa() is True
    assert acc_current.is_isa() is False

def test_opened_in_current_tax_year():
    tax_year_start = date(2025, 6, 4)
    
    acc1 = Account(account_number=1007, user_id="USR007", account_type="Cash ISA", account_balance=500.0, opened_date=date(2025, 6, 5))
    acc2 = Account(account_number=1008, user_id="USR008", account_type="Cash ISA", account_balance=500.0, opened_date=date(2025, 5, 30))
    
    assert acc1.opened_in_current_tax_year(tax_year_start) is True
    assert acc2.opened_in_current_tax_year(tax_year_start) is False
