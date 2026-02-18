import sys
from pathlib import Path
# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))
from unittest.mock import MagicMock
import pytest



from models.user import User
from repositories.user_repository import UserRepository
from services.user_service import UserService


@pytest.fixture
def mock_user_repo():
    repo = MagicMock(spec=UserRepository)
    # Sample user object for testing
    repo.get_user_by_id.return_value = User(
        user_id="USR001",
        name="John Smith",
        age=35,
        uk_resident=True,
        crown_servant=False,
        crown_servant_spouse=False
    )

    # Add get_all_users mock so _generate_user_id() works
    repo.get_all_users.return_value = [repo.get_user_by_id.return_value]
    return repo



@pytest.fixture
def user_service(mock_user_repo, tmp_path):
    # Use a temporary CSV path so no real file is written
    csv_file = tmp_path / "users.csv"
    return UserService(user_repository=mock_user_repo, csv_path=csv_file)


def test_get_user(user_service, mock_user_repo):
    user = user_service.get_user("USR001")
    assert user.user_id == "USR001"
    assert user.name == "John Smith"
    mock_user_repo.get_user_by_id.assert_called_once_with("USR001")


def test_create_user(user_service):
    new_user = user_service.create_user(
        name="Alice Johnson",
        age=28,
        uk_resident=True,
        crown_servant=False,
        crown_servant_spouse=True
    )

    # The new user ID should start with "USR"
    assert new_user.user_id.startswith("USR")
    assert new_user.name == "Alice Johnson"
    assert new_user.age == 28
    assert new_user.uk_resident is True
    assert new_user.crown_servant is False
    assert new_user.crown_servant_spouse is True

    # The CSV file should now exist
    assert user_service.csv_path.exists()

    # Check CSV contains header + new user row
    with open(user_service.csv_path, newline="", encoding="utf-8") as f:
        lines = f.read().splitlines()
        assert lines[0].startswith("user_id")  # header
        assert "Alice Johnson" in lines[1]


def test_get_accounts_for_user_returns_none_if_user_not_found(user_service, mock_user_repo):
    # Make get_user return None
    mock_user_repo.get_user_by_id.return_value = None
    accounts = user_service.get_accounts_for_user("USR999")
    assert accounts is None
