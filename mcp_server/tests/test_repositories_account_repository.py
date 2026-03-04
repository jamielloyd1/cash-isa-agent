# mcp_server/tests/test_repositories_account_repository.py
import sys
from pathlib import Path
from datetime import date
import pytest
from unittest.mock import mock_open, patch

sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.account import Account
from repositories.account_repository import AccountRepository
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from src/repositories
sys.path.insert(0, str(PROJECT_ROOT))

from config import USERS_CSV, ACCOUNTS_CSV, TRANSACTIONS_CSV

# Sample CSV content
CSV_CONTENT = """account_number,user_id,account_type,account_balance,opened_date
1001,USR001,Cash ISA,5000.0,2025-07-01
1002,USR001,Current Account,1500.0,2024-12-15
1003,USR002,Cash ISA,8000.0,2025-01-20
"""


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_all_accounts(mock_file):
    # Use the config path to match new repository signature
    repo = AccountRepository(csv_path=ACCOUNTS_CSV)
    accounts = repo.get_all_accounts()

    assert len(accounts) == 3
    assert all(isinstance(acc, Account) for acc in accounts)
    assert accounts[0].account_number == 1001
    assert accounts[1].account_type == "Current Account"


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_account_by_number_exists(mock_file):
    repo = AccountRepository(csv_path=ACCOUNTS_CSV)
    account = repo.get_account_by_number(1002)

    assert account is not None
    assert account.account_number == 1002
    assert account.user_id == "USR001"
    assert account.account_type == "Current Account"


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_account_by_number_not_exists(mock_file):
    repo = AccountRepository(csv_path=ACCOUNTS_CSV)
    account = repo.get_account_by_number(9999)

    assert account is None


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_accounts_by_user_id(mock_file):
    repo = AccountRepository(csv_path=ACCOUNTS_CSV)
    accounts_usr1 = repo.get_accounts_by_user_id("USR001")
    accounts_usr2 = repo.get_accounts_by_user_id("USR002")
    accounts_usr3 = repo.get_accounts_by_user_id("NONEXISTENT")

    assert len(accounts_usr1) == 2
    assert accounts_usr1[0].account_number == 1001
    assert len(accounts_usr2) == 1
    assert accounts_usr2[0].account_number == 1003
    assert len(accounts_usr3) == 0