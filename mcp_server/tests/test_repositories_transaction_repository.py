# mcp_server/tests/test_repositories_transaction_repository.py
import sys
from pathlib import Path
from datetime import date
import pytest
from unittest.mock import mock_open, patch

# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.transaction import Transaction
from repositories.transaction_repository import TransactionRepository

# Sample CSV content for mocking
CSV_CONTENT = """transaction_id,account_number,user_id,amount,date,type
1,1001,USR001,5000.0,2025-07-01,opening_deposit
2,1001,USR001,1000.0,2025-07-05,contribution
3,1002,USR002,2000.0,2025-06-15,opening_deposit
4,1001,USR001,500.0,2025-07-10,contribution
"""


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_transaction_by_id_exists(mock_file):
    repo = TransactionRepository(csv_path="fake_path.csv")
    txn = repo.get_transaction_by_id(2)

    assert txn is not None
    assert txn.transaction_id == "2"
    assert txn.account_number == 1001
    assert txn.user_id == "USR001"
    assert txn.amount == 1000.0
    assert txn.date == date(2025, 7, 5)
    assert txn.type == "contribution"


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_transaction_by_id_not_exists(mock_file):
    repo = TransactionRepository(csv_path="fake_path.csv")
    txn = repo.get_transaction_by_id(999)

    assert txn is None


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_transactions_by_account_number(mock_file):
    repo = TransactionRepository(csv_path="fake_path.csv")
    txns = repo.get_transactions_by_account_number(1001)

    assert len(txns) == 3
    assert all(isinstance(txn, Transaction) for txn in txns)
    assert txns[0].transaction_id == "1"
    assert txns[1].type == "contribution"


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_transactions_by_user_id(mock_file):
    repo = TransactionRepository(csv_path="fake_path.csv")
    txns_usr1 = repo.get_transactions_by_user_id("USR001")
    txns_usr2 = repo.get_transactions_by_user_id("USR002")
    txns_nonexistent = repo.get_transactions_by_user_id("NONEXISTENT")

    assert len(txns_usr1) == 3
    assert all(txn.user_id == "USR001" for txn in txns_usr1)
    assert len(txns_usr2) == 1
    assert txns_usr2[0].account_number == 1002
    assert len(txns_nonexistent) == 0
