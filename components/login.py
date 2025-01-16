# app/components/login.py

import streamlit as st
from utils.auth import verify_password
from utils.data_manager import DataManager

class LoginComponent:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def show_login(self):
        """Display login form and handle authentication"""
        st.title("Leave Management System")
        
        # Create login form
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if username in self.data_manager.users:
                    user = self.data_manager.users[username]
                    if verify_password(user.password, password):
                        # Set session state
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.session_state['is_admin'] = user.is_admin
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid password!")
                else:
                    st.error("Username not found!")

        # Add some basic information about the system
        with st.expander("About the System"):
            st.write("""
            This is a Leave Management System where you can:
            - Request leaves
            - Track leave status
            - View leave calendar
            - Check leave balance
            """)