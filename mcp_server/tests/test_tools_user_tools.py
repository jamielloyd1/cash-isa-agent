import sys
from pathlib import Path
# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))
import pytest
from unittest.mock import MagicMock
from tools.user_tools import UserTools
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
def user_tools(mock_user_service, mock_cash_isa_account_service):
    return UserTools(
        user_service=mock_user_service,
        cash_isa_account_service=mock_cash_isa_account_service
    )


# ---------- get_user_details Tests ----------

def test_get_user_details_success(user_tools, mock_user_service):
    # Arrange
    mock_user = MagicMock()
    mock_user.user_id = "USR001"
    mock_user.name = "Jamie"
    mock_user.age = 30
    mock_user.uk_resident = True
    mock_user.crown_servant = False
    mock_user.crown_servant_spouse = False

    mock_user_service.get_user.return_value = mock_user

    # Act
    result = user_tools.get_user_details("USR001")

    # Assert
    assert result["success"] is True
    assert result["user_id"] == "USR001"
    assert result["name"] == "Jamie"
    assert result["age"] == 30
    assert result["uk_resident"] is True
    assert result["crown_servant"] is False
    assert result["crown_servant_spouse"] is False

    mock_user_service.get_user.assert_called_once_with("USR001")


def test_get_user_details_not_found(user_tools, mock_user_service):
    # Arrange
    mock_user_service.get_user.return_value = None

    # Act
    result = user_tools.get_user_details("USR999")

    # Assert
    assert result["success"] is False
    assert result["error"] == "User not found."
    mock_user_service.get_user.assert_called_once_with("USR999")


def test_get_user_details_exception(user_tools, mock_user_service):
    # Arrange
    mock_user_service.get_user.side_effect = Exception("Database failure")

    # Act
    result = user_tools.get_user_details("USR001")

    # Assert
    assert result["success"] is False
    assert result["error"] == "Database failure"


# ---------- create_user Tests ----------

def test_create_user_success(user_tools, mock_user_service):
    # Arrange
    mock_new_user = MagicMock()
    mock_new_user.user_id = "USR123"

    mock_user_service.create_user.return_value = mock_new_user

    # Act
    result = user_tools.create_user(
        name="Jamie",
        age=30,
        uk_resident=True,
        crown_servant=False,
        crown_servant_spouse=False
    )

    # Assert
    assert result["success"] is True
    assert result["user_id"] == "USR123"
    assert result["message"] == "User created successfully."

    mock_user_service.create_user.assert_called_once_with(
        "Jamie", 30, True, False, False
    )


def test_create_user_exception(user_tools, mock_user_service):
    # Arrange
    mock_user_service.create_user.side_effect = Exception("Creation failed")

    # Act
    result = user_tools.create_user(
        name="Jamie",
        age=30,
        uk_resident=True,
        crown_servant=False,
        crown_servant_spouse=False
    )

    # Assert
    assert result["success"] is False
    assert result["error"] == "Creation failed"
