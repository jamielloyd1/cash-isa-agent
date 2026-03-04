from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
USERS_CSV = DATA_DIR / "users" / "users.csv"
ACCOUNTS_CSV = DATA_DIR / "users" / "accounts.csv"
TRANSACTIONS_CSV = DATA_DIR / "users" / "transactions.csv"