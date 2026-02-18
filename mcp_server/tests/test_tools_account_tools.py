# tests/test_tools_account_tools.py
import sys
from pathlib import Path
from datetime import date
from unittest.mock import MagicMock
import pytest

# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tools.account_tools import AccountTools
from services.user_service import UserService
from services.cash_isa_account_service import CashISAAccountService

# --- Fixtures ---

@pytest.fixture
def mock_user_service():
    service = MagicMock(spec=UserService)
    service.get_accounts_for_user.return_value = [
        MagicMock(account_number=1001, account_type="current", balance=500.0, opened_date=date(2023, 1, 1)),
        MagicMock(account_number=1002, account_type="savings", balance=1500.0, opened_date=date(2022, 6, 15)),
    ]
    return service

@pytest.fixture
def mock_cash_isa_service():
    service = MagicMock(spec=CashISAAccountService)
    service.open_cash_isa.return_value = MagicMock(account_number=2001)
    return service

@pytest.fixture
def account_tools(mock_user_service, mock_cash_isa_service):
    return AccountTools(user_service=mock_user_service, cash_isa_account_service=mock_cash_isa_service)

# --- Tests ---

def test_get_all_account_details_success(account_tools, mock_user_service):
    user_id = "USR001"
    result = account_tools.get_all_account_details(user_id)

    assert result["success"] is True
    assert len(result["accounts"]) == 2
    assert result["accounts"][0]["account_number"] == 1001
    assert result["accounts"][1]["balance"] == 1500.0
    mock_user_service.get_accounts_for_user.assert_called_once_with(user_id)

def test_get_all_account_details_failure(account_tools, mock_user_service):
    user_id = "USR002"
    mock_user_service.get_accounts_for_user.side_effect = Exception("Database error")

    result = account_tools.get_all_account_details(user_id)
    assert result["success"] is False
    assert result["error"] == "Database error"

def test_open_cash_isa_success(account_tools, mock_cash_isa_service):
    user_id = "USR001"
    deposit = 1000.0

    result = account_tools.open_cash_isa(user_id, deposit)

    assert result["success"] is True
    assert result["account_number"] == 2001
    assert result["message"] == "Cash ISA opened successfully."
    mock_cash_isa_service.open_cash_isa.assert_called_once_with(user_id, deposit)

def test_open_cash_isa_value_error(account_tools, mock_cash_isa_service):
    user_id = "USR001"
    deposit = 1000.0
    mock_cash_isa_service.open_cash_isa.side_effect = ValueError("Deposit too low")

    result = account_tools.open_cash_isa(user_id, deposit)

    assert result["success"] is False
    assert result["error"] == "Deposit too low"

def test_open_cash_isa_unexpected_error(account_tools, mock_cash_isa_service):
    user_id = "USR001"
    deposit = 1000.0
    mock_cash_isa_service.open_cash_isa.side_effect = RuntimeError("Unexpected failure")

    result = account_tools.open_cash_isa(user_id, deposit)

    assert result["success"] is False
    assert result["error"] == "Unexpected error occurred while opening account."
