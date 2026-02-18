# mcp_server/tests/test_models_transaction.py
import sys
from pathlib import Path
from datetime import date
import pytest

# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.transaction import Transaction  # import your Transaction class


def test_transaction_creation():
    txn = Transaction(
        transaction_id="TXN001",
        account_number=1001,
        user_id="USR001",
        amount=5000.0,
        date=date(2025, 7, 10),
        type="opening_deposit"
    )
    
    assert txn.transaction_id == "TXN001"
    assert txn.account_number == 1001
    assert txn.user_id == "USR001"
    assert txn.amount == 5000.0
    assert txn.date == date(2025, 7, 10)
    assert txn.type == "opening_deposit"


def test_is_contribution_true():
    txn = Transaction(
        transaction_id="TXN002",
        account_number=1001,
        user_id="USR001",
        amount=2000.0,
        date=date(2025, 7, 11),
        type="contribution"
    )
    assert txn.is_contribution() is True
    assert txn.is_opening_deposit() is False


def test_is_opening_deposit_true():
    txn = Transaction(
        transaction_id="TXN003",
        account_number=1002,
        user_id="USR002",
        amount=3000.0,
        date=date(2025, 7, 12),
        type="opening_deposit"
    )
    assert txn.is_opening_deposit() is True
    assert txn.is_contribution() is False


def test_str_method():
    txn = Transaction(
        transaction_id="TXN004",
        account_number=1003,
        user_id="USR003",
        amount=1500.0,
        date=date(2025, 7, 13),
        type="contribution"
    )
    expected_str = "Transaction(TXN004: £1500.0 on 2025-07-13)"
    assert str(txn) == expected_str
