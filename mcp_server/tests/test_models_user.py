# mcp_server/tests/test_models_user.py
import sys
from pathlib import Path
import pytest

# Add src folder to sys.path so Python can find modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.user import User  # import your User class


def test_user_creation():
    user = User(
        user_id="USR001",
        name="John Smith",
        age=35,
        uk_resident=True,
        crown_servant=False,
        crown_servant_spouse=False
    )
    
    assert user.user_id == "USR001"
    assert user.name == "John Smith"
    assert user.age == 35
    assert user.uk_resident is True
    assert user.crown_servant is False
    assert user.crown_servant_spouse is False


def test_user_str():
    user = User(
        user_id="USR002",
        name="Jane Doe",
        age=28,
        uk_resident=True,
        crown_servant=True,
        crown_servant_spouse=False
    )
    expected_str = "User(USR002: Jane Doe, age 28)"
    assert str(user) == expected_str


def test_user_flags():
    user = User(
        user_id="USR003",
        name="Bob Johnson",
        age=42,
        uk_resident=False,
        crown_servant=False,
        crown_servant_spouse=True
    )
    
    # Test boolean fields
    assert user.uk_resident is False
    assert user.crown_servant is False
    assert user.crown_servant_spouse is True
