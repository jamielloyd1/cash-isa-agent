# mcp_server/tests/test_repositories_user_repository.py
import sys
from pathlib import Path
import pytest
from unittest.mock import mock_open, patch

# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.user import User
from repositories.user_repository import UserRepository

# Sample CSV content for mocking
CSV_CONTENT = """user_id,name,age,uk_resident,crown_servant,crown_servant_spouse
USR001,John Smith,35,True,False,False
USR002,Jane Doe,28,True,True,False
USR003,Bob Johnson,42,False,False,True
"""


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_all_users(mock_file):
    repo = UserRepository(csv_path="fake_path.csv")
    users = repo.get_all_users()

    assert len(users) == 3
    assert all(isinstance(user, User) for user in users)
    assert users[0].user_id == "USR001"
    assert users[1].name == "Jane Doe"
    assert users[2].crown_servant_spouse is True


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_user_by_id_exists(mock_file):
    repo = UserRepository(csv_path="fake_path.csv")
    user = repo.get_user_by_id("USR002")

    assert user is not None
    assert user.user_id == "USR002"
    assert user.name == "Jane Doe"
    assert user.age == 28
    assert user.uk_resident is True
    assert user.crown_servant is True
    assert user.crown_servant_spouse is False


@patch("pathlib.Path.open", new_callable=lambda: mock_open(read_data=CSV_CONTENT))
def test_get_user_by_id_not_exists(mock_file):
    repo = UserRepository(csv_path="fake_path.csv")
    user = repo.get_user_by_id("NONEXISTENT")

    assert user is None
