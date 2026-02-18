
import sys
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import Mock
import pytest

# Add the src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.account import Account
from models.transaction import Transaction
from services.cash_isa_account_service import CashISAAccountService

# ------------------------------
# Fixtures for mocks
# ------------------------------
@pytest.fixture
def mock_user_repo():
    return Mock()


@pytest.fixture
def mock_account_repo():
    repo = Mock()
    repo.get_all_accounts.return_value = []
    repo.get_account_by_number.side_effect = lambda acct_num: None
    repo.get_accounts_by_user_id.return_value = []  # FIX: iterable for tax year checks
    return repo


@pytest.fixture
def mock_transaction_repo():
    repo = Mock()
    repo.get_transactions_by_user_id.return_value = []
    repo.get_all_transactions.return_value = []
    return repo


@pytest.fixture
def eligibility_policy():
    return Mock(minimum_age=18)


@pytest.fixture
def contribution_policy():
    today = date.today()
    if today >= date(today.year, 4, 6):
        start = date(today.year, 4, 6)
        end = date(today.year + 1, 4, 5)
    else:
        start = date(today.year - 1, 4, 6)
        end = date(today.year, 4, 5)

    policy = Mock(tax_year_start=start, tax_year_end=end)
    return policy


@pytest.fixture
def service(mock_user_repo, mock_account_repo, mock_transaction_repo, eligibility_policy, contribution_policy):
    return CashISAAccountService(
        user_repo=mock_user_repo,
        account_repo=mock_account_repo,
        transaction_repo=mock_transaction_repo,
        eligibility_policy=eligibility_policy,
        contribution_policy=contribution_policy,
        accounts_csv_path="test_accounts.csv",
        transactions_csv_path="test_transactions.csv"
    )

# ------------------------------
# Test eligibility checks
# ------------------------------
def test_meets_eligibility(service, mock_user_repo):
    user = Mock(age=20, uk_resident=True, crown_servant=False, crown_servant_spouse=False)
    assert service._meets_eligibility_requirements(user) is True

    user.age = 16
    assert service._meets_eligibility_requirements(user) is False

    user.age = 25
    user.uk_resident = False
    user.crown_servant = False
    user.crown_servant_spouse = False
    assert service._meets_eligibility_requirements(user) is False

# ------------------------------
# Test tax year rules
# ------------------------------
def test_opened_this_tax_year(service):
    today = date.today()
    account = Mock(opened_date=today)
    service.contribution_policy.tax_year_start = today - timedelta(days=1)
    service.contribution_policy.tax_year_end = today + timedelta(days=1)
    assert service._opened_this_tax_year(account) is True

    account.opened_date = today - timedelta(days=365)
    assert service._opened_this_tax_year(account) is False

# ------------------------------
# Test contribution checks
# ------------------------------
def test_has_contributed_to_cash_isa_this_tax_year(service, mock_transaction_repo, mock_account_repo):
    user_id = "USR001"

    # Ensure UK tax year covers today
    today = date.today()
    if today >= date(today.year, 4, 6):
        service.contribution_policy.tax_year_start = date(today.year, 4, 6)
        service.contribution_policy.tax_year_end = date(today.year + 1, 4, 5)
    else:
        service.contribution_policy.tax_year_start = date(today.year - 1, 4, 6)
        service.contribution_policy.tax_year_end = date(today.year, 4, 5)

    txn = Transaction(transaction_id="TXN001", account_number=1000, user_id=user_id, amount=100, date=today, type="contribution")
    mock_transaction_repo.get_transactions_by_user_id.return_value = [txn]

    cash_isa_account = Account(account_number=1000, user_id=user_id, account_type="Cash ISA", account_balance=100, opened_date=today)
    
    # Use side_effect instead of return_value
    def account_side_effect(account_number):
        if account_number == 1000:
            return cash_isa_account
        return None
    mock_account_repo.get_account_by_number.side_effect = account_side_effect

    assert service._has_contributed_to_cash_isa_this_tax_year(user_id) is True

    # Test with non-Cash ISA account
    cash_isa_account.account_type = "Other"
    assert service._has_contributed_to_cash_isa_this_tax_year(user_id) is False


def test_has_contributed_20k_to_isas_this_tax_year(service, mock_transaction_repo, mock_account_repo):
    user_id = "USR001"

    txn1 = Transaction(transaction_id="TXN001", account_number=1000, user_id=user_id, amount=10000, date=date.today(), type="contribution")
    txn2 = Transaction(transaction_id="TXN002", account_number=1001, user_id=user_id, amount=10000, date=date.today(), type="contribution")
    mock_transaction_repo.get_transactions_by_user_id.return_value = [txn1, txn2]

    def account_side_effect(num):
        if num == 1000:
            return Account(account_number=1000, user_id=user_id, account_type="Cash ISA", account_balance=0, opened_date=date.today())
        if num == 1001:
            return Account(account_number=1001, user_id=user_id, account_type="Lifetime ISA", account_balance=0, opened_date=date.today())
        return None

    mock_account_repo.get_account_by_number.side_effect = account_side_effect

    assert service._has_contributed_20k_to_isas_this_tax_year(user_id) is True

    # Test below 20k
    txn2.amount = 5000
    assert service._has_contributed_20k_to_isas_this_tax_year(user_id) is False

# ------------------------------
# Test account opening
# ------------------------------
def test_open_cash_isa(service, mock_user_repo, mock_account_repo, mock_transaction_repo):
    user_id = "USR001"
    mock_user_repo.get_user_by_id.return_value = Mock(age=30, uk_resident=True, crown_servant=False, crown_servant_spouse=False)

    mock_account_repo.save_account = Mock()
    mock_transaction_repo.save_transaction = Mock()
    mock_account_repo.get_all_accounts.return_value = []
    mock_account_repo.get_accounts_by_user_id.return_value = []  # FIX: iterable for tax year checks

    account = service.open_cash_isa(user_id, 5000)
    assert account.account_type == "Cash ISA"
    assert account.account_balance == 5000
    assert isinstance(account.opened_date, date)
