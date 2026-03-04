import sys
from pathlib import Path
from unittest.mock import MagicMock
from datetime import date
import pytest

# Ensure project src folder is on path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Correct imports
from services.cash_isa_contribution_service import CashISAContributionService, ContributionCheckResult
from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.cash_isa_policy import CashISAEligibilityPolicy, CashISAContributionPolicy  # <-- import policies

# -----------------------
# Fixtures
# -----------------------
@pytest.fixture
def user_repo():
    repo = MagicMock()
    repo.get_user_by_id.side_effect = lambda user_id: {"user_id": user_id} if user_id != "missing" else None
    return repo

@pytest.fixture
def account_repo():
    repo = MagicMock()
    repo.get_accounts_by_user_id.side_effect = lambda user_id: [
        Account(account_number=1000, user_id=user_id, account_type="Cash ISA", balance=5000),
        Account(account_number=1001, user_id=user_id, account_type="Current Account", balance=2000)
    ] if user_id != "nocash" else []
    repo._update_account_balance = MagicMock()
    return repo

@pytest.fixture
def transaction_repo():
    repo = MagicMock()
    repo.get_transactions_by_account_number.side_effect = lambda acc_no: []
    repo.save_transaction = MagicMock()
    return repo

@pytest.fixture
def eligibility_policy():
    return CashISAEligibilityPolicy()

@pytest.fixture
def contribution_policy():
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    return CashISAContributionPolicy(tax_year_start=start_of_year, annual_limit_all_isas=20000)

@pytest.fixture
def service(user_repo, account_repo, transaction_repo, eligibility_policy, contribution_policy):
    return CashISAContributionService(
        user_repo, account_repo, transaction_repo, eligibility_policy, contribution_policy
    )

# -----------------------
# Eligibility Tests
# -----------------------
def test_can_contribute_user_missing(service):
    result = service.can_contribute_to_cash_isa("missing")
    assert result.can_contribute is False
    assert result.reason == "User not found."

def test_can_contribute_no_cash_isa(service):
    result = service.can_contribute_to_cash_isa("nocash")
    assert result.can_contribute is False
    assert result.reason == "User does not have a Cash ISA account."

def test_can_contribute_success(service):
    result = service.can_contribute_to_cash_isa("USR001")
    assert result.can_contribute is True
    assert result.reason is None

# -----------------------
# Contribution rules tests
# -----------------------
def test_has_contributed_to_different_cash_isa(service, monkeypatch):
    monkeypatch.setattr(service, "_get_cash_isa_accounts_contributed_this_tax_year", lambda user_id: [9999])
    valid, reason = service._has_contributed_to_different_cash_isa_this_year("USR001", 1000)
    assert valid is False
    assert reason == "User has already contributed to a different Cash ISA this tax year."

def test_has_not_contributed_to_different_cash_isa(service, monkeypatch):
    monkeypatch.setattr(service, "_get_cash_isa_accounts_contributed_this_tax_year", lambda user_id: [1000])
    valid, reason = service._has_contributed_to_different_cash_isa_this_year("USR001", 1000)
    assert valid is True
    assert reason is None

# -----------------------
# Contribution remaining
# -----------------------
def test_contribution_amount_remaining_for_tax_year_no_prior_contributions(service):
    remaining, eligible_accounts = service.contribution_amount_remaining_for_tax_year("USR001")
    assert remaining == 20000
    assert eligible_accounts == [1000]

def test_contribution_amount_remaining_for_tax_year_with_prior_contributions(service, monkeypatch):
    past_txn = Transaction(
        transaction_id="TXN0001",
        account_number=1000,
        user_id="USR001",
        amount=5000,
        date=date.today(),
        type="contribution"
    )
    monkeypatch.setattr(service.transaction_repo, "get_transactions_by_account_number", lambda acc_no: [past_txn] if acc_no == 1000 else [])
    remaining, eligible_accounts = service.contribution_amount_remaining_for_tax_year("USR001")
    assert remaining == 15000
    assert eligible_accounts == [1000]

# -----------------------
# make_contribution tests
# -----------------------
def test_make_contribution_success(service, monkeypatch):
    monkeypatch.setattr(service, "_get_cash_isa_accounts_contributed_this_tax_year", lambda user_id: [])
    monkeypatch.setattr(service.account_service, "generate_transaction_id", lambda: "TXN0001")
    result = service.make_contribution(user_id="USR001", account_number=1000, amount=1000)
    assert result is True
    service.account_service.transaction_repo.save_transaction.assert_called_once()
    service.account_service.account_repo._update_account_balance.assert_called_once_with(1000, 1000)

def test_make_contribution_negative_amount(service):
    with pytest.raises(ValueError, match="Contribution amount must be positive."):
        service.make_contribution("USR001", 1000, -100)

def test_make_contribution_exceeds_allowance(service, monkeypatch):
    monkeypatch.setattr(service, "_get_cash_isa_accounts_contributed_this_tax_year", lambda user_id: [])
    monkeypatch.setattr(service.transaction_repo, "get_transactions_by_account_number",
                        lambda acc_no: [Transaction("TXN0001", acc_no, "USR001", 20000, date.today(), "contribution")])
    with pytest.raises(ValueError, match="Contribution amount exceeds remaining allowance"):
        service.make_contribution("USR001", 1000, 1000)

def test_make_contribution_wrong_account(service, monkeypatch):
    monkeypatch.setattr(service, "_get_cash_isa_accounts_contributed_this_tax_year", lambda user_id: [])
    with pytest.raises(ValueError, match="This account is not eligible for contributions this tax year."):
        service.make_contribution("USR001", 1002, 1000)

def test_make_contribution_user_ineligible(service, monkeypatch):
    monkeypatch.setattr(service, "can_contribute_to_cash_isa", lambda uid, acc=None: ContributionCheckResult(False, "Not allowed"))
    with pytest.raises(ValueError, match="Not allowed"):
        service.make_contribution("USR001", 1000, 1000)