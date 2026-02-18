import sys
from pathlib import Path
# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))
import pytest
from unittest.mock import MagicMock
from tools.eligibility_tools import EligibilityTools
from services.user_service import UserService
from services.cash_isa_account_service import CashISAAccountService


# ---------- Fixtures ----------

@pytest.fixture
def mock_user_service():
    return MagicMock(spec=UserService)


@pytest.fixture
def mock_cash_isa_account_service():
    return MagicMock(spec=CashISAAccountService)


@pytest.fixture
def eligibility_tools(mock_user_service, mock_cash_isa_account_service):
    return EligibilityTools(
        user_service=mock_user_service,
        cash_isa_account_service=mock_cash_isa_account_service
    )


# ---------- Tests ----------

def test_check_cash_isa_eligibility_true(eligibility_tools, mock_cash_isa_account_service):
    # Arrange
    mock_cash_isa_account_service.can_open_cash_isa.return_value = True

    # Act
    result = eligibility_tools.check_cash_isa_eligibility("USR001")

    # Assert
    assert result["success"] is True
    assert result["eligible"] is True
    assert result["message"] == "User is eligible to open a Cash ISA account."
    mock_cash_isa_account_service.can_open_cash_isa.assert_called_once_with("USR001")


def test_check_cash_isa_eligibility_false(eligibility_tools, mock_cash_isa_account_service):
    # Arrange
    mock_cash_isa_account_service.can_open_cash_isa.return_value = False

    # Act
    result = eligibility_tools.check_cash_isa_eligibility("USR002")

    # Assert
    assert result["success"] is True
    assert result["eligible"] is False
    assert result["message"] == "User is not eligible to open a Cash ISA account."
    mock_cash_isa_account_service.can_open_cash_isa.assert_called_once_with("USR002")


def test_check_cash_isa_eligibility_exception(eligibility_tools, mock_cash_isa_account_service):
    # Arrange
    mock_cash_isa_account_service.can_open_cash_isa.side_effect = Exception("Service failure")

    # Act
    result = eligibility_tools.check_cash_isa_eligibility("USR003")

    # Assert
    assert result["success"] is False
    assert result["error"] == "Service failure"
