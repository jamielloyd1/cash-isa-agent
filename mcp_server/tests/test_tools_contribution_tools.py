# tests/test_tools_contribution_tools.py
import sys
from pathlib import Path
# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))
import pytest
from unittest.mock import MagicMock
from services.cash_isa_contribution_service import ContributionCheckResult
from tools.contribution_tools import ContributionTools


@pytest.fixture
def mock_user_service():
    return MagicMock()


@pytest.fixture
def mock_cash_isa_account_service():
    return MagicMock()


@pytest.fixture
def mock_cash_isa_contribution_service():
    return MagicMock()


@pytest.fixture
def contribution_tools(mock_user_service, mock_cash_isa_account_service, mock_cash_isa_contribution_service):
    return ContributionTools(
        user_service=mock_user_service,
        cash_isa_account_service=mock_cash_isa_account_service,
        cash_isa_contribution_service=mock_cash_isa_contribution_service
    )


def test_check_contribution_eligibility_success(contribution_tools, mock_cash_isa_contribution_service):
    # Setup
    mock_cash_isa_contribution_service.can_contribute_to_cash_isa.return_value = ContributionCheckResult(
        can_contribute=True,
        reason=None
    )

    result = contribution_tools.check_contribution_eligibility("USR001", 1000)

    assert result["success"] is True
    assert result["can_contribute"] is True
    assert result["reason"] is None
    mock_cash_isa_contribution_service.can_contribute_to_cash_isa.assert_called_once_with("USR001", 1000)


def test_check_contribution_eligibility_failure(contribution_tools, mock_cash_isa_contribution_service):
    # Setup an exception in the service
    mock_cash_isa_contribution_service.can_contribute_to_cash_isa.side_effect = Exception("Service error")

    result = contribution_tools.check_contribution_eligibility("USR001")

    assert result["success"] is False
    assert "Service error" in result["error"]


def test_check_contribution_amount_remaining(contribution_tools, mock_cash_isa_contribution_service):
    # Setup
    mock_cash_isa_contribution_service.contribution_amount_remaining_for_tax_year.return_value = (5000.0, [1000, 2000])

    result = contribution_tools.check_contribution_amount("USR001", 1000)

    assert result["success"] is True
    assert result["can_contribute"] is True
    assert result["contribution_amount"] == 5000.0
    assert result["eligible_accounts"] == [1000, 2000]


def test_check_contribution_amount_none_remaining(contribution_tools, mock_cash_isa_contribution_service):
    # Setup no remaining allowance
    mock_cash_isa_contribution_service.contribution_amount_remaining_for_tax_year.return_value = (0.0, ["User has no remaining contribution allowance for this tax year."])

    result = contribution_tools.check_contribution_amount("USR001", 1000)

    assert result["success"] is True
    assert result["can_contribute"] is False
    assert "User has no remaining contribution allowance" in result["reason"]


def test_contribute_to_cash_isa_success(contribution_tools, mock_cash_isa_contribution_service):
    # Setup service to succeed
    mock_cash_isa_contribution_service.make_contribution.return_value = True

    result = contribution_tools.contribute_to_cash_isa("USR001", 1000, 1500.0)

    assert result["success"] is True
    assert "Successfully contributed £1500.00" in result["message"]
    mock_cash_isa_contribution_service.make_contribution.assert_called_once_with("USR001", 1000, 1500.0)


def test_contribute_to_cash_isa_value_error(contribution_tools, mock_cash_isa_contribution_service):
    # Raise ValueError when amount invalid
    mock_cash_isa_contribution_service.make_contribution.side_effect = ValueError("Contribution exceeds limit")

    result = contribution_tools.contribute_to_cash_isa("USR001", 1000, 1500.0)

    assert result["success"] is False
    assert "Contribution exceeds limit" in result["error"]


def test_contribute_to_cash_isa_unexpected_error(contribution_tools, mock_cash_isa_contribution_service):
    # Raise generic Exception
    mock_cash_isa_contribution_service.make_contribution.side_effect = Exception("Unexpected failure")

    result = contribution_tools.contribute_to_cash_isa("USR001", 1000, 1500.0)

    assert result["success"] is False
    assert "Unexpected failure" in result["error"]
