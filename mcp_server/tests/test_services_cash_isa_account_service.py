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
# Fixtures
# ------------------------------

@pytest.fixture
def mock_user_repo():
    return Mock()


@pytest.fixture
def mock_account_repo():
    repo = Mock()
    repo.get_all_accounts.return_value = []
    repo.get_account_by_number.return_value = None
    repo.get_accounts_by_user_id.return_value = []
    repo.save_account = Mock()
    return repo


@pytest.fixture
def mock_transaction_repo():
    repo = Mock()
    repo.get_transactions_by_user_id.return_value = []
    repo.get_all_transactions.return_value = []
    repo.save_transaction = Mock()
    return repo


@pytest.fixture
def eligibility_policy():
    return Mock(minimum_age=18)


@pytest.fixture
def contribution_policy():
    """Always generate a correct UK tax year around today."""
    today = date.today()

    if today >= date(today.year, 4, 6):
        start = date(today.year, 4, 6)
        end = date(today.year + 1, 4, 5)
    else:
        start = date(today.year - 1, 4, 6)
        end = date(today.year, 4, 5)

    return Mock(tax_year_start=start, tax_year_end=end)


@pytest.fixture
def service(
    mock_user_repo,
    mock_account_repo,
    mock_transaction_repo,
    eligibility_policy,
    contribution_policy,
):
    return CashISAAccountService(
        user_repo=mock_user_repo,
        account_repo=mock_account_repo,
        transaction_repo=mock_transaction_repo,
        eligibility_policy=eligibility_policy,
        contribution_policy=contribution_policy,
    )


# ------------------------------
# Eligibility Tests
# ------------------------------

def test_meets_eligibility(service):
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
# Tax Year Tests
# ------------------------------

def test_opened_this_tax_year(service):
    today = date.today()

    service.contribution_policy.tax_year_start = today - timedelta(days=1)
    service.contribution_policy.tax_year_end = today + timedelta(days=1)

    account = Mock(opened_date=today)
    assert service._opened_this_tax_year(account) is True

    account.opened_date = today - timedelta(days=365)
    assert service._opened_this_tax_year(account) is False


# ------------------------------
# Contribution Tests
# ------------------------------

def test_has_contributed_to_cash_isa_this_tax_year(
    service, mock_transaction_repo, mock_account_repo
):
    user_id = "USR001"
    today = date.today()

    txn = Transaction(
        transaction_id="TXN001",
        account_number=1000,
        user_id=user_id,
        amount=100,
        date=today,
        type="contribution",
    )

    mock_transaction_repo.get_transactions_by_user_id.return_value = [txn]

    cash_isa_account = Account(
        account_number=1000,
        user_id=user_id,
        account_type="Cash ISA",
        account_balance=100,
        opened_date=today,
    )

    mock_account_repo.get_account_by_number.side_effect = (
        lambda acct_num: cash_isa_account if acct_num == 1000 else None
    )

    assert service._has_contributed_to_cash_isa_this_tax_year(user_id) is True

    # Change account type
    cash_isa_account.account_type = "Other"
    assert service._has_contributed_to_cash_isa_this_tax_year(user_id) is False


def test_has_contributed_20k_to_isas_this_tax_year(
    service, mock_transaction_repo, mock_account_repo
):
    user_id = "USR001"
    today = date.today()

    txn1 = Transaction("TXN001", 1000, user_id, 10000, today, "contribution")
    txn2 = Transaction("TXN002", 1001, user_id, 10000, today, "contribution")

    mock_transaction_repo.get_transactions_by_user_id.return_value = [txn1, txn2]

    def account_lookup(account_number):
        if account_number == 1000:
            return Account(1000, user_id, "Cash ISA", 0, today)
        if account_number == 1001:
            return Account(1001, user_id, "Lifetime ISA", 0, today)
        return None

    mock_account_repo.get_account_by_number.side_effect = account_lookup

    assert service._has_contributed_20k_to_isas_this_tax_year(user_id) is True

    # Reduce total below 20k
    txn2.amount = 5000
    assert service._has_contributed_20k_to_isas_this_tax_year(user_id) is False


# ------------------------------
# Account Opening Test
# ------------------------------

def test_open_cash_isa(
    service, mock_user_repo, mock_account_repo, mock_transaction_repo
):
    user_id = "USR001"

    mock_user_repo.get_user_by_id.return_value = Mock(
        age=30,
        uk_resident=True,
        crown_servant=False,
        crown_servant_spouse=False,
    )

    account = service.open_cash_isa(user_id, 5000)

    assert account.account_type == "Cash ISA"
    assert account.account_balance == 5000
    assert isinstance(account.opened_date, date)

    mock_account_repo.save_account.assert_called_once()
    mock_transaction_repo.save_transaction.assert_called_once()