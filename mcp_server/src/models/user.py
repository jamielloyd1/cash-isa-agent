from dataclasses import dataclass

@dataclass
class User:
    """
    Represents a real person in the Cash ISA system.
    
    These fields come directly from users.csv
    """
    
    user_id: str                    # Unique identifier (e.g., "USR001")
    name: str                       # User's full name (e.g., "John Smith")
    age: int                        # How old they are (e.g., 35)
    uk_resident: bool               # Are they a UK resident? (True/False)
    crown_servant: bool             # Are they a UK Crown servant? (True/False)
    crown_servant_spouse: bool      # Are they married to a Crown servant? (True/False)
    
    def __str__(self):
        return f"User({self.user_id}: {self.name}, age {self.age})"
    