# app/components/user.py

import streamlit as st
from datetime import date, timedelta
import pandas as pd
from utils.data_manager import DataManager
from models.leave import LeaveRequest
from config import LEAVE_TYPES

class UserComponent:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def show_leave_request_form(self):
        """Display leave request form"""
        st.subheader("Request Leave")

        # Get current user
        user = self.data_manager.users[st.session_state['username']]

        # Show current leave balance
        st.write("### Your Leave Balance")
        balance_df = pd.DataFrame([user.leave_balance]).T
        balance_df.columns = ['Days Available']
        st.dataframe(balance_df)

        # Calculate date ranges
        today = date.today()
        min_date = today + timedelta(days=7)  # Minimum 7 days in advance
        max_date = today + timedelta(days=365)  # Maximum 1 year in advance

        # Date selection outside the form
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Start Date",
                value=min_date if 'leave_start_date' not in st.session_state else st.session_state.leave_start_date,
                min_value=min_date,
                max_value=max_date,
                key='start_date_input',
                on_change=self.update_dates
            )

        with col2:
            end_date = st.date_input(
                "End Date",
                value=max(start_date, min_date if 'leave_end_date' not in st.session_state else st.session_state.leave_end_date),
                min_value=start_date,
                max_value=max_date,
                key='end_date_input',
                on_change=self.update_dates
            )

        # Update session state
        st.session_state.leave_start_date = start_date
        st.session_state.leave_end_date = end_date

        # Calculate duration
        duration = (end_date - start_date).days + 1
        st.write(f"**Duration:** {duration} days")

        # Create leave request form
        with st.form("leave_request_form"):
            # Leave type selection
            leave_type = st.selectbox(
                "Leave Type",
                options=list(LEAVE_TYPES.keys()),
                format_func=lambda x: f"{x} - {LEAVE_TYPES[x]}"
            )

            # Show current balance for selected leave type
            current_balance = user.leave_balance[leave_type]
            st.write(f"**Available {leave_type} Balance:** {current_balance} days")

            # Reason input
            reason = st.text_area("Reason for Leave", height=100)

            submitted = st.form_submit_button("Submit Request")

            if submitted:
                # Validate inputs
                if not reason.strip():
                    st.error("Please provide a reason for your leave request!")
                    return

                if duration > current_balance:
                    st.error(f"Insufficient {leave_type} balance! You have {current_balance} days available.")
                    return

                # Create leave request
                leave_request = LeaveRequest(
                    id="",  # Will be set by data manager
                    username=user.username,
                    start_date=start_date,
                    end_date=end_date,
                    leave_type=leave_type,
                    reason=reason
                )

                # Save request
                if self.data_manager.add_leave_request(leave_request):
                    st.success("Leave request submitted successfully!")
                    # Show request details
                    st.write("### Request Details:")
                    st.write(f"Duration: {duration} days")
                    st.write(f"Leave Type: {leave_type}")
                    st.write(f"Start Date: {start_date}")
                    st.write(f"End Date: {end_date}")
                    
                    # Reset form
                    st.session_state.leave_start_date = min_date
                    st.session_state.leave_end_date = min_date
                    
                    # Add a refresh button
                    if st.button("Submit Another Request"):
                        st.rerun()
                else:
                    st.error("Error submitting leave request!")

        # Show existing requests
        self.show_my_leaves()
    
    def update_dates(self):
        """Callback function to handle date changes"""
        st.rerun()

    def show_my_leaves(self):
        """Display user's leave history"""
        st.subheader("My Leaves")

        # Get user's leaves
        leaves = self.data_manager.get_user_leaves(st.session_state['username'])

        if not leaves:
            st.info("No leave requests found.")
            return

        # Create tabs for different views
        tab1, tab2 = st.tabs(["Active Requests", "Leave History"])

        with tab1:
            active_leaves = [leave for leave in leaves 
                        if leave.status == "Pending" or 
                        (leave.status == "Approved" and leave.end_date >= date.today())]
            if active_leaves:
                for leave in active_leaves:
                    duration = (leave.end_date - leave.start_date).days + 1
                    with st.expander(f"{leave.leave_type}: {leave.start_date} to {leave.end_date} ({duration} days)"):
                        st.write(f"**Status:** {leave.status}")
                        st.write(f"**Reason:** {leave.reason}")
                        if leave.admin_comment:
                            st.write(f"**Admin Comment:** {leave.admin_comment}")
            else:
                st.info("No active leave requests.")

        with tab2:
            if leaves:
                leaves_df = pd.DataFrame([
                    {
                        'Start Date': leave.start_date,
                        'End Date': leave.end_date,
                        'Duration': (leave.end_date - leave.start_date).days + 1,
                        'Type': leave.leave_type,
                        'Status': leave.status,
                        'Reason': leave.reason,
                        'Comment': leave.admin_comment or ''
                    }
                    for leave in leaves
                ])
                
                st.dataframe(
                    leaves_df.sort_values('Start Date', ascending=False),
                    use_container_width=True
                )
            else:
                st.info("No leave history found.")