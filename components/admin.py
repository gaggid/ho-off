# app/components/admin.py

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils.data_manager import DataManager
from utils.auth import hash_password
from models.user import User
from config import LEAVE_TYPES, DEFAULT_LEAVE_BALANCE

class AdminComponent:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def show_pending_requests(self):
        """Display and manage pending leave requests"""
        st.subheader("Pending Leave Requests")
        
        pending_leaves = self.data_manager.get_pending_leaves()
        
        if not pending_leaves:
            st.info("No pending leave requests.")
            return

        for leave in pending_leaves:
            # Calculate duration directly
            duration = (leave.end_date - leave.start_date).days + 1
            
            with st.expander(f"{leave.username}: {leave.leave_type} ({leave.start_date} to {leave.end_date})"):
                st.write(f"**Duration:** {duration} days")
                st.write(f"**Reason:** {leave.reason}")
                
                # Get user's leave balance
                user = self.data_manager.users[leave.username]
                st.write(f"**Current {leave.leave_type} Balance:** {user.leave_balance[leave.leave_type]} days")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"approve_{leave.id}"):
                        # Update leave balance
                        user.leave_balance[leave.leave_type] -= duration
                        # Update leave status
                        self.data_manager.update_leave_request(leave.id, "Approved")
                        self.data_manager.save_data()
                        st.success("Leave approved!")
                        st.experimental_rerun()

                with col2:
                    # Create a unique key for each leave's rejection section
                    rejection_key = f"reject_{leave.id}"
                    if rejection_key not in st.session_state:
                        st.session_state[rejection_key] = {
                            'show_comment': False,
                            'comment': ''
                        }

                    if st.button("Reject", key=f"reject_btn_{leave.id}"):
                        st.session_state[rejection_key]['show_comment'] = True

                    # Show comment input if reject was clicked
                    if st.session_state[rejection_key]['show_comment']:
                        comment = st.text_input(
                            "Rejection Reason",
                            key=f"comment_input_{leave.id}"
                        )
                        if st.button("Confirm Rejection", key=f"confirm_reject_{leave.id}"):
                            if comment.strip():
                                self.data_manager.update_leave_request(leave.id, "Rejected", comment)
                                self.data_manager.save_data()
                                st.success("Leave rejected!")
                                st.experimental_rerun()
                            else:
                                st.error("Please provide a reason for rejection")

    def manage_users(self):
        """User management interface"""
        st.subheader("Manage Users")

        # Add new user section
        with st.expander("Add New User"):
            with st.form("add_user_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                email = st.text_input("Email")
                department = st.text_input("Department")
                
                # Add admin user option
                is_admin = st.checkbox("Create as Admin User")
                
                # Show leave balance only for non-admin users
                leave_balance = None  # Will use default from User model
                if not is_admin:
                    st.write("Initial Leave Balance")
                    leave_balance = {}
                    cols = st.columns(len(DEFAULT_LEAVE_BALANCE))
                    for i, (leave_type, default_value) in enumerate(DEFAULT_LEAVE_BALANCE.items()):
                        with cols[i]:
                            leave_balance[leave_type] = st.number_input(
                                leave_type,
                                min_value=0,
                                value=default_value
                            )

                if st.form_submit_button("Add User"):
                    if username and password and email:
                        # Check if username already exists
                        if username in self.data_manager.users:
                            st.error("Username already exists!")
                            return

                        # Create user object
                        user = User(
                            username=username,
                            password=hash_password(password),
                            email=email,
                            department=department,
                            leave_balance=leave_balance,
                            is_admin=is_admin
                        )

                        if self.data_manager.add_user(user):
                            st.success(f"{'Admin' if is_admin else 'User'} added successfully!")
                        else:
                            st.error("Error adding user!")
                    else:
                        st.error("Please fill all required fields!")

        # User list and management
        st.subheader("Existing Users")

        # Create separate tables for regular users and admins
        users_data = {
            'regular': [],
            'admin': []
        }

        for username, user in self.data_manager.users.items():
            user_data = {
                'Username': username,
                'Email': user.email,
                'Department': user.department
            }
            
            if user.is_admin:
                users_data['admin'].append(user_data)
            else:
                users_data['regular'].append({**user_data, **user.leave_balance})

        # Display admin users
        st.write("### Admin Users")
        if users_data['admin']:
            admin_df = pd.DataFrame(users_data['admin'])
            st.dataframe(admin_df)
        else:
            st.info("No additional admin users.")

        # Display regular users
        st.write("### Regular Users")
        if users_data['regular']:
            users_df = pd.DataFrame(users_data['regular'])
            st.dataframe(users_df)
        else:
            st.info("No regular users.")

        # User deletion
        st.write("### Delete User")
        # Get all usernames except the current admin
        deletable_users = [username for username, user in self.data_manager.users.items() 
                        if username != st.session_state['username']]

        if deletable_users:
            user_to_delete = st.selectbox(
                "Select user to delete",
                options=deletable_users
            )
            
            if st.button("Delete User"):
                # Add confirmation checkbox
                confirm = st.checkbox("I confirm that I want to delete this user")
                if confirm:
                    # Check if trying to delete the last admin
                    if self.data_manager.users[user_to_delete].is_admin:
                        admin_count = sum(1 for user in self.data_manager.users.values() if user.is_admin)
                        if admin_count <= 1:
                            st.error("Cannot delete the last admin user!")
                            return

                    del self.data_manager.users[user_to_delete]
                    self.data_manager.save_data()
                    st.success(f"User {user_to_delete} deleted!")
                    st.experimental_rerun()
                elif st.button("Delete", type="primary"):
                    st.warning("Please confirm deletion by checking the box above")

    def show_reports(self):
        """Generate and display various reports"""
        st.subheader("Leave Reports")

        # Create tabs for different reports
        tab1, tab2, tab3 = st.tabs(["Leave Usage", "Department Analysis", "Leave Patterns"])

        with tab1:
            self._show_leave_usage_report()

        with tab2:
            self._show_department_analysis()

        with tab3:
            self._show_leave_patterns()
    
    def show_data_management(self):
        """Display data management options"""
        st.subheader("Data Management")
        
        # Backup section
        st.write("### Backup Options")
        if st.button("Create Backup"):
            if self.data_manager.create_backup():
                st.success("Backup created successfully!")
            else:
                st.error("Failed to create backup!")
        
        # Danger zone for data purge
        st.write("### ⚠️ Danger Zone")
        with st.expander("Purge All Data"):
            st.warning("""
            Warning: This action will permanently delete all data except the admin account.
            This includes:
            - All user accounts
            - All leave requests
            - All holiday records
            
            This action cannot be undone!
            """)
            
            # Create two columns for confirmation
            col1, col2 = st.columns(2)
            
            with col1:
                confirm_text = st.text_input(
                    "Type 'CONFIRM' to proceed with data purge",
                    key="purge_confirm"
                )
            
            with col2:
                if st.button("Purge All Data", type="primary", key="purge_button"):
                    if confirm_text == "CONFIRM":
                        # Create backup before purging
                        if self.data_manager.create_backup():
                            if self.data_manager.purge_data():
                                st.success("All data has been purged successfully!")
                                # Add a rerun button to refresh the page
                                if st.button("Refresh Page"):
                                    st.experimental_rerun()
                            else:
                                st.error("Error occurred while purging data!")
                        else:
                            st.error("Failed to create backup before purging!")
                    else:
                        st.error("Please type 'CONFIRM' to proceed with data purge")

    def _show_leave_usage_report(self):
        """Display leave usage report"""
        # Calculate leave usage for each user
        usage_data = []
        for username, user in self.data_manager.users.items():
            if not user.is_admin:
                user_leaves = self.data_manager.get_user_leaves(username)
                approved_leaves = [leave for leave in user_leaves if leave.status == "Approved"]
                
                for leave_type in LEAVE_TYPES:
                    total_days = sum((leave.end_date - leave.start_date).days + 1 
                                    for leave in approved_leaves 
                                    if leave.leave_type == leave_type)
                    usage_data.append({
                        'Username': username,
                        'Leave Type': leave_type,
                        'Days Used': total_days,
                        'Balance': user.leave_balance[leave_type]
                    })

        if usage_data:
            df = pd.DataFrame(usage_data)
            fig = px.bar(df, x='Username', y=['Days Used', 'Balance'],
                        barmode='group', title='Leave Usage vs Balance')
            st.plotly_chart(fig)
        else:
            st.info("No leave data available.")
    
    def show_data_management(self):
        """Display data management options"""
        st.subheader("Data Management")

        with st.expander("⚠️ Danger Zone"):
            st.warning("""
            Warning: This action will permanently delete all data except the admin account.
            This includes:
            - All user accounts
            - All leave requests
            - All holiday records
            
            This action cannot be undone!
            """)
            
            # Create two columns for confirmation
            col1, col2 = st.columns(2)
            
            with col1:
                confirm_text = st.text_input(
                    "Type 'CONFIRM' to proceed with data purge",
                    key="purge_confirm"
                )
            
            with col2:
                if st.button("Purge All Data", type="primary", key="purge_button"):
                    if confirm_text == "CONFIRM":
                        if self.data_manager.purge_data():
                            st.success("All data has been purged successfully!")
                            # Add a rerun button to refresh the page
                            if st.button("Refresh Page"):
                                st.experimental_rerun()
                        else:
                            st.error("Error occurred while purging data!")
                    else:
                        st.error("Please type 'CONFIRM' to proceed with data purge")

    def _show_department_analysis(self):
        """Display department-wise leave analysis"""
        dept_data = {}
        for username, user in self.data_manager.users.items():
            if not user.is_admin:
                if user.department not in dept_data:
                    dept_data[user.department] = {'total_days': 0, 'users': 0}
                dept_data[user.department]['users'] += 1
                
                user_leaves = self.data_manager.get_user_leaves(username)
                approved_leaves = [leave for leave in user_leaves if leave.status == "Approved"]
                total_days = sum((leave.end_date - leave.start_date).days + 1 
                                for leave in approved_leaves)
                dept_data[user.department]['total_days'] += total_days

        if dept_data:
            df = pd.DataFrame([
                {
                    'Department': dept,
                    'Average Days': data['total_days'] / data['users'],
                    'Total Users': data['users']
                }
                for dept, data in dept_data.items()
            ])
            
            fig = px.bar(df, x='Department', y='Average Days',
                        title='Average Leave Days by Department')
            st.plotly_chart(fig)
        else:
            st.info("No department data available.")

    def _show_leave_patterns(self):
        """Display leave patterns analysis"""
        all_leaves = [leave for leave in self.data_manager.leave_requests 
                    if leave.status == "Approved"]
        
        if all_leaves:
            # Create monthly pattern
            monthly_data = []
            for leave in all_leaves:
                duration = (leave.end_date - leave.start_date).days + 1
                monthly_data.append({
                    'Month': leave.start_date.strftime('%B'),
                    'Days': duration
                })
            
            df = pd.DataFrame(monthly_data)
            monthly_summary = df.groupby('Month')['Days'].sum().reset_index()
            
            fig = px.line(monthly_summary, x='Month', y='Days',
                        title='Monthly Leave Patterns')
            st.plotly_chart(fig)
        else:
            st.info("No leave pattern data available.")