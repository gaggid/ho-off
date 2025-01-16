# app/models/leave.py

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class LeaveRequest:
    id: str
    username: str
    start_date: date
    end_date: date
    leave_type: str
    reason: str
    status: str = "Pending"
    admin_comment: str = ""
    request_date: datetime = None
    action_date: datetime = None

    def __post_init__(self):
        if self.request_date is None:
            self.request_date = datetime.now()

@property
def duration(self) -> int:
    """Calculate the duration of the leave in days"""
    return (self.end_date - self.start_date).days + 1

def get_duration(self) -> int:
    """Alternative method to get duration"""
    return (self.end_date - self.start_date).days + 1