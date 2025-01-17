# app/utils/data_manager.py

import pickle
from typing import List, Dict
import uuid
from datetime import datetime
from config import USERS_FILE, LEAVES_FILE, HOLIDAYS_FILE
from models.user import User
from models.leave import LeaveRequest

class DataManager:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.leave_requests: List[LeaveRequest] = []
        self.holidays: List[dict] = []
        self.load_data()
    
    def update_user(self, username: str, user_data: dict) -> bool:
        """Update user information"""
        if username in self.users:
            user = self.users[username]
            
            # Update email if provided
            if 'email' in user_data:
                user.email = user_data['email']
                
            # Update department if provided
            if 'department' in user_data:
                user.department = user_data['department']
                
            # Update password if provided
            if 'password' in user_data and user_data['password']:
                user.password = user_data['password']
                
            # Update leave balance if provided
            if 'leave_balance' in user_data and not user.is_admin:
                user.leave_balance = user_data['leave_balance']
            
            self.save_data()
            return True
        return False

    def delete_user(self, username: str) -> bool:
        """Delete a user and their associated leave requests"""
        if username in self.users:
            # Delete user
            del self.users[username]
            
            # Delete associated leave requests
            self.leave_requests = [leave for leave in self.leave_requests 
                                if leave.username != username]
            
            self.save_data()
            return True
        return False

    def get_user(self, username: str) -> User:
        """Get user by username"""
        return self.users.get(username)

    def load_data(self):
        """Load data from pickle files"""
        try:
            if USERS_FILE.exists():
                with open(USERS_FILE, 'rb') as f:
                    self.users = pickle.load(f)
            
            if LEAVES_FILE.exists():
                with open(LEAVES_FILE, 'rb') as f:
                    self.leave_requests = pickle.load(f)
            
            if HOLIDAYS_FILE.exists():
                with open(HOLIDAYS_FILE, 'rb') as f:
                    self.holidays = pickle.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")

    def save_data(self):
        """Save data to pickle files"""
        try:
            with open(USERS_FILE, 'wb') as f:
                pickle.dump(self.users, f)
            
            with open(LEAVES_FILE, 'wb') as f:
                pickle.dump(self.leave_requests, f)
            
            with open(HOLIDAYS_FILE, 'wb') as f:
                pickle.dump(self.holidays, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_user(self, user: User) -> bool:
        """Add a new user"""
        if user.username not in self.users:
            self.users[user.username] = user
            self.save_data()
            return True
        return False

    def add_leave_request(self, leave_request: LeaveRequest) -> bool:
        """Add a new leave request"""
        leave_request.id = str(uuid.uuid4())
        self.leave_requests.append(leave_request)
        self.save_data()
        return True
    
    def create_backup(self):
        """Create a backup of current data"""
        from datetime import datetime
        import shutil
        import os

        backup_dir = os.path.join(os.path.dirname(self.users_file), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            # Backup each file
            for filename in [self.users_file, self.leaves_file, self.holidays_file]:
                if os.path.exists(filename):
                    backup_file = os.path.join(
                        backup_dir,
                        f"{os.path.basename(filename)}_{timestamp}.bak"
                    )
                    shutil.copy2(filename, backup_file)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

        def restore_backup(self, timestamp):
            """Restore data from a backup"""
            import os

            backup_dir = os.path.join(os.path.dirname(self.users_file), 'backups')
            try:
                # Restore each file
                for filename in [self.users_file, self.leaves_file, self.holidays_file]:
                    backup_file = os.path.join(
                        backup_dir,
                        f"{os.path.basename(filename)}_{timestamp}.bak"
                    )
                    if os.path.exists(backup_file):
                        shutil.copy2(backup_file, filename)
                
                # Reload data
                self.load_data()
                return True
            except Exception as e:
                print(f"Restore failed: {e}")
                return False

    def purge_data(self):
        """Purge all data and reinitialize with default admin"""
        from utils.auth import create_admin_user  # Import here to avoid circular import

        # Reset data structures
        self.users = {'admin': create_admin_user()}
        self.leave_requests = []
        self.holidays = []

        # Save empty data
        self.save_data()

        return True

    def update_leave_request(self, leave_id: str, status: str, comment: str = "") -> bool:
        """Update leave request status"""
        for leave in self.leave_requests:
            if leave.id == leave_id:
                leave.status = status
                leave.admin_comment = comment
                leave.action_date = datetime.now()
                self.save_data()
                return True
        return False

    def get_user_leaves(self, username: str) -> List[LeaveRequest]:
        """Get all leave requests for a user"""
        return [leave for leave in self.leave_requests if leave.username == username]

    def get_pending_leaves(self) -> List[LeaveRequest]:
        """Get all pending leave requests"""
        return [leave for leave in self.leave_requests if leave.status == "Pending"]