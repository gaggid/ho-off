from dataclasses import dataclass
from typing import Dict
from config import DEFAULT_LEAVE_BALANCE

@dataclass
class User:
    username: str
    password: str  # Stored as hash
    email: str
    department: str
    leave_balance: Dict[str, int] = None
    is_admin: bool = False
    

    def __post_init__(self):
        if self.leave_balance is None:
            self.leave_balance = DEFAULT_LEAVE_BALANCE.copy()