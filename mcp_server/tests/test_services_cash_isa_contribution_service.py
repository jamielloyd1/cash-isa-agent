import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from datetime import date, timedelta
import pytest

# Add src folder to sys.path
sys.path.append(str(Path(__file__).parent.parent / "src"))


from services.cash_isa_contribution_service import CashISAContributionService, ContributionCheckResult
from models import User, Account, Transaction
from services.cash_isa_account_service import CashISAAccountService


@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.get_user_by_id.return_value = User(
        user_id="USR001",
        name="John Doe",
        age=30,
        uk_resident=True,
        crown_servant=False,
        crown_servant_spouse=False
    )
    return repo

@pytest.fixture
def mock_account_repo():
    repo = MagicMock()
    repo.get_accounts_by_user_id.return_value = [
        Account(account_number=1000, user_id="USR001", account_type="cash_isa", account_balance=5000, opened_date=date.today()),
        Account(account_number=1001, user_id="USR001", account_type="Lifetime ISA", account_balance=2000, opened_date=date.today())
    ]
    return repo

@pytest.fixture
def mock_transaction_repo():
    repo = MagicMock()
    repo.get_transactions_by_account_number.return_value = []
    return repo

@pytest.fixture
def eligibility_policy():
    return Mock()

@pytest.fixture
def contribution_policy():
    policy = Mock()
    policy.annual_limit_all_isas = 20000
    policy.tax_year_start = date(date.today().year if date.today().month >= 4 else date.today().year-1, 4, 6)
    return policy

@pytest.fixture
def service(mock_user_repo, mock_account_repo, mock_transaction_repo, eligibility_policy, contribution_policy):
    return CashISAContributionService(
        user_repo=mock_user_repo,
        account_repo=mock_account_repo,
        transaction_repo=mock_transaction_repo,
        eligibility_policy=eligibility_policy,
        contribution_policy=contribution_policy
    )

# ---------------------------
# Public API tests
# ---------------------------
def test_can_contribute_to_cash_isa_success(service):
    result = service.can_contribute_to_cash_isa("USR001")
    assert isinstance(result, ContributionCheckResult)
    assert result.can_contribute is True

def test_contribution_amount_remaining_for_tax_year(service, mock_transaction_repo):
    remaining, accounts = service.contribution_amount_remaining_for_tax_year("USR001")
    assert remaining == 20000
    assert 1000 in accounts

# ---------------------------
# Internal helper tests
# ---------------------------
def test_get_cash_isa_accounts_contributed_this_tax_year(service, mock_transaction_repo):
    # Simulate one contribution
    txn = Transaction(transaction_id="TXN001", account_number=1000, user_id="USR001", amount=100, date=date.today(), type="contribution")
    mock_transaction_repo.get_transactions_by_account_number.return_value = [txn]
    contributed_accounts = service._get_cash_isa_accounts_contributed_this_tax_year("USR001")
    assert 1000 in contributed_accounts

def test_has_contributed_to_different_cash_isa_this_year(service, mock_transaction_repo):
    # Account 1000 already contributed
    txn = Transaction(transaction_id="TXN001", account_number=1000, user_id="USR001", amount=100, date=date.today(), type="contribution")
    mock_transaction_repo.get_transactions_by_account_number.return_value = [txn]
    valid, reason = service._has_contributed_to_different_cash_isa_this_year("USR001", 1001)
    assert valid is False
    assert reason is not None

# ---------------------------
# make_contribution tests
# ---------------------------
def test_make_contribution_success(service, monkeypatch):
    # Patch _get_cash_isa_accounts_contributed_this_tax_year to prevent contribution conflicts
    monkeypatch.setattr(service, "_get_cash_isa_accounts_contributed_this_tax_year", lambda user_id: [])

    # Patch CashISAAccountService instance methods to avoid CSV writes and ID issues
    monkeypatch.setattr(CashISAAccountService, "save_transaction", lambda self, t: True)
    monkeypatch.setattr(CashISAAccountService, "_update_account_balance", lambda self, a, b: True)
    monkeypatch.setattr(CashISAAccountService, "generate_transaction_id", lambda self: "TXN999")

    # Now call make_contribution
    result = service.make_contribution(user_id="USR001", account_number=1000, amount=1000)
    assert result is True


def test_make_contribution_too_high(service, mock_transaction_repo, monkeypatch):
    # Fill contributions to max
    mock_transaction_repo.get_transactions_by_account_number.return_value = [
        Transaction(transaction_id="TXN001", account_number=1000, user_id="USR001", amount=20000, date=date.today(), type="contribution")
    ]
    # Patch can_contribute_to_cash_isa to allow contribution logic to run
    monkeypatch.setattr(service, "can_contribute_to_cash_isa", lambda user_id: ContributionCheckResult(True))
    
    import pytest
    with pytest.raises(ValueError, match="Contribution amount exceeds remaining allowance"):
        service.make_contribution(user_id="USR001", account_number=1000, amount=1000)