# app/config.py

import os
from pathlib import Path

# Page configuration
PAGE_CONFIG = {
"page_title": "Leave Management System",
"page_icon": "📅",
"layout": "wide",
"initial_sidebar_state": "expanded",
"menu_items": {
    'Get Help': 'https://www.example.com/help',
    'Report a bug': "https://www.example.com/bug",
    'About': "# Leave Management System\nVersion 1.0"
}
}

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"

# Create data directory if it doesn't exist
if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True)

# Data file paths
USERS_FILE = DATA_DIR / "users.pkl"
LEAVES_FILE = DATA_DIR / "leaves.pkl"
HOLIDAYS_FILE = DATA_DIR / "holidays.pkl"

# Leave types
LEAVE_TYPES = {
'EL': 'Earned Leave',
'CL': 'Casual Leave',
'SL': 'Sick Leave',
'OH': 'Optional Holiday'
}

# Default leave balance
DEFAULT_LEAVE_BALANCE = {
'EL': 12,
'CL': 12,
'SL': 12,
'OH': 2
}

# Add these color configurations
LEAVE_TYPE_COLORS = {
'EL': '#FFE6E6',  # Light red
'CL': '#E6F3FF',  # Light blue
'SL': '#FFE6FF',  # Light purple
'OH': '#E6FFE6',  # Light green
'Holiday': '#FFF2E6'  # Light orange
}

# Add theme configuration
STREAMLIT_THEME = {
"theme": {
    "base": "light",
    "primaryColor": "#FF4B4B",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F0F2F6",
    "textColor": "#262730",
    "font": "sans serif"
}
}

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Passw0rd@911"  # In production, use environment variables