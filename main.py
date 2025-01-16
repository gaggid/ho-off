# app/main.py

import streamlit as st
from config import STREAMLIT_THEME, PAGE_CONFIG
from utils.data_manager import DataManager
from components.login import LoginComponent
from components.calendar_view import CalendarView
from components.user import UserComponent
from components.admin import AdminComponent
from utils.auth import create_admin_user

# Set page configuration
st.set_page_config(**PAGE_CONFIG)

# Apply custom theme
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
    }
    .stSelectbox {
        background-color: #F0F2F6;
    }
    .stTextInput {
        background-color: #F0F2F6;
    }
    .stDateInput {
        background-color: #F0F2F6;
    }
    .stTextArea {
        background-color: #F0F2F6;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    session_state_vars = {
        'logged_in': False,
        'username': None,
        'is_admin': False
    }

    for var, default_value in session_state_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

class LeaveManagementApp:
    def __init__(self):
        # Initialize session state
        init_session_state()
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Create admin user if not exists
        if 'admin' not in self.data_manager.users:
            self.data_manager.add_user(create_admin_user())
            self.data_manager.save_data()

        # Initialize components
        self.login_component = LoginComponent(self.data_manager)
        self.calendar_view = CalendarView(self.data_manager)
        self.user_component = UserComponent(self.data_manager)
        self.admin_component = AdminComponent(self.data_manager)

    def show_logout_button(self):
        """Display logout button in sidebar"""
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.session_state['is_admin'] = False
            st.experimental_rerun()

    def run(self):
        """Run the main application"""
        try:
            if not st.session_state['logged_in']:
                self.login_component.show_login()
            else:
                self.show_logout_button()
                
                # Show different views based on user type
                if st.session_state['is_admin']:
                    self.show_admin_view()
                else:
                    self.show_user_view()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            init_session_state()
            st.experimental_rerun()

    def show_admin_view(self):
        """Display admin dashboard"""
        st.title(f"Welcome, {st.session_state['username']} (Admin)")

        menu = st.sidebar.selectbox(
            "Menu",
            ["Calendar", "Pending Requests", "Manage Users", "Reports", "Data Management"]
        )

        if menu == "Calendar":
            self.calendar_view.show_calendar()
        elif menu == "Pending Requests":
            self.admin_component.show_pending_requests()
        elif menu == "Manage Users":
            self.admin_component.manage_users()
        elif menu == "Reports":
            self.admin_component.show_reports()
        elif menu == "Data Management":
            self.admin_component.show_data_management()

    def show_user_view(self):
        """Display user dashboard"""
        st.title(f"Welcome, {st.session_state['username']}")
        
        menu = st.sidebar.selectbox(
            "Menu",
            ["Calendar", "Request Leave", "My Leaves"]
        )

        if menu == "Calendar":
            self.calendar_view.show_calendar()
        elif menu == "Request Leave":
            self.user_component.show_leave_request_form()
        elif menu == "My Leaves":
            self.user_component.show_my_leaves()

if __name__ == "__main__":
    app = LeaveManagementApp()
    app.run()