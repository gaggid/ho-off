# app/components/calendar_view.py

import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
from utils.data_manager import DataManager
from collections import defaultdict
from config import LEAVE_TYPE_COLORS

class CalendarView:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def get_month_leaves(self, year: int, month: int):
        """Get all leaves and holidays for the month"""
        daily_leaves = defaultdict(list)
        
        # Add approved leaves
        for leave in self.data_manager.leave_requests:
            if leave.status == "Approved":
                current = leave.start_date
                while current <= leave.end_date:
                    if current.year == year and current.month == month:
                        daily_leaves[current].append({
                            'username': leave.username,
                            'type': leave.leave_type,
                            'start_date': leave.start_date,
                            'end_date': leave.end_date
                        })
                    current += timedelta(days=1)

        # Add holidays
        for holiday in self.data_manager.holidays:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            if holiday_date.year == year and holiday_date.month == month:
                daily_leaves[holiday_date].append({
                    'type': 'Holiday',
                    'description': holiday['description']
                })

        return daily_leaves

    def create_calendar_table(self, year: int, month: int, daily_leaves):
        """Create calendar table data"""
        # Get the calendar for the specified month
        cal = calendar.monthcalendar(year, month)
        
        # Initialize data structures
        header = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        dates = []
        leaves = []
        colors = []
        
        # Process each week
        for week in cal:
            week_dates = []
            week_leaves = []
            week_colors = []
            
            for day_idx, day in enumerate(week):
                if day == 0:
                    week_dates.append("")
                    week_leaves.append("")
                    week_colors.append("white")
                else:
                    current_date = date(year, month, day)
                    
                    # Format date string with better visibility
                    date_text = f"<b>{day}</b><br>{current_date.strftime('%a')}"
                    week_dates.append(date_text)
                    
                    # Get leave information with color coding
                    leave_text = []
                    if current_date in daily_leaves:
                        leave_count = defaultdict(int)
                        holiday_text = None
                        
                        for leave in daily_leaves[current_date]:
                            if leave.get('type') == 'Holiday':
                                color = LEAVE_TYPE_COLORS['Holiday']
                                holiday_text = f"<span style='background-color: {color}; padding: 2px 4px; border-radius: 3px;'>🏖️ {leave['description']}</span>"
                            else:
                                leave_count[leave['type']] += 1
                        
                        if holiday_text:
                            leave_text.append(holiday_text)
                        
                        for leave_type, count in leave_count.items():
                            color = LEAVE_TYPE_COLORS.get(leave_type, '#FFFFFF')
                            leave_text.append(
                                f"<span style='background-color: {color}; padding: 2px 4px; border-radius: 3px;'>{count} {leave_type}</span>"
                            )
                    
                    week_leaves.append("<br>".join(leave_text) if leave_text else "")
                    
                    # Set cell color
                    week_colors.append('#FFFFD4' if day_idx >= 5 else 'white')
            
            dates.append(week_dates)
            leaves.append(week_leaves)
            colors.append(week_colors)
        
        return header, dates, leaves, colors
    def show_calendar(self):
        """Display the calendar view"""
        st.subheader("Leave Calendar")

        # Date selection
        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox("Year", 
                                    range(date.today().year, date.today().year + 2),
                                    index=0)
        with col2:
            selected_month = st.selectbox("Month",
                                        range(1, 13),
                                        index=date.today().month - 1,
                                        format_func=lambda x: calendar.month_name[x])

        # Get leave data
        daily_leaves = self.get_month_leaves(selected_year, selected_month)

        # Create calendar data
        header, dates, leaves, colors = self.create_calendar_table(selected_year, selected_month, daily_leaves)

        # # Debug output
        # if st.checkbox("Show Debug Information"):
        #     st.write("### Debug Information")
        #     st.write("Header:", header)
        #     st.write("Dates:", dates)
        #     st.write("Leaves:", leaves)
        #     st.write("Colors:", colors)

        # Create calendar visualization
        fig = go.Figure()

        # Combine dates and leaves data
        combined_data = []
        for week_dates, week_leaves in zip(dates, leaves):
            week_data = []
            for date_text, leave_text in zip(week_dates, week_leaves):
                if date_text and leave_text:
                    cell_text = f"{date_text}<br>{leave_text}"
                elif date_text:
                    cell_text = date_text
                else:
                    cell_text = ""
                week_data.append(cell_text)
            combined_data.append(week_data)

        # Transpose the data for proper display
        combined_data = list(map(list, zip(*combined_data)))
        colors_data = list(map(list, zip(*colors)))

        # Create single table with combined data
        fig.add_trace(go.Table(
            header=dict(
                values=header,
                fill_color='paleturquoise',
                align='center',
                height=40,
                font=dict(size=14, color='black')
            ),
            cells=dict(
                values=combined_data,
                fill_color=colors_data,
                align='center',
                height=80,  # Increased height to accommodate both date and leave info
                font=dict(size=12),
                format=['<br>'.join(str(x).split('\n')) for x in combined_data]
            )
        ))

        # Update layout
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            height=600,
            showlegend=False
        )

        # Display calendar
        st.plotly_chart(fig, use_container_width=True)

        # Show legend
        st.write("### Legend")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Calendar Colors:**")
            st.markdown("⬜ Weekdays")
            st.markdown('<span style="background-color: #FFFFD4; padding: 2px 8px;">Weekends</span>', 
                    unsafe_allow_html=True)
            st.markdown("🏖️ Holidays")
        
        with col2:
            st.markdown("**Leave Types:**")
            for leave_type, color in LEAVE_TYPE_COLORS.items():
                st.markdown(
                    f'<span style="background-color: {color}; padding: 2px 8px; border-radius: 3px;">{leave_type}</span>',
                    unsafe_allow_html=True
                )

        # Show month summary
        self._show_month_summary(daily_leaves)

    def _show_month_summary(self, daily_leaves):
        """Display month summary information"""
        st.subheader("Month Summary")
        
        if not daily_leaves:
            st.info("No leaves scheduled for this month")
            return

        # Create summary by date
        summary_data = []
        for current_date, leaves in sorted(daily_leaves.items()):
            total_leaves = 0
            unique_users = set()
            
            for leave in leaves:
                if leave.get('type') != 'Holiday':
                    total_leaves += 1
                    unique_users.add(leave['username'])
            
            if total_leaves > 0:
                summary_data.append({
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Day': current_date.strftime('%A'),
                    'Total Leaves': total_leaves,
                    'Users on Leave': len(unique_users)
                })

        if summary_data:
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

            # Show leave type totals
            st.subheader("Leave Type Summary")
            leave_counts = defaultdict(lambda: {'total_days': 0, 'employees': set()})
            
            for date_leaves in daily_leaves.values():
                for leave in date_leaves:
                    if leave.get('type') != 'Holiday':
                        leave_type = leave['type']
                        leave_counts[leave_type]['total_days'] += 1
                        leave_counts[leave_type]['employees'].add(leave['username'])

            summary_stats = [{
                'Leave Type': leave_type,
                'Total Days': stats['total_days'],
                'Total Employees': len(stats['employees']),
                'Employees': ', '.join(sorted(stats['employees']))
            } for leave_type, stats in leave_counts.items()]

            if summary_stats:
                st.dataframe(pd.DataFrame(summary_stats), use_container_width=True)