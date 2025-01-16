# Leave Management System

A streamlined web application built with Streamlit for managing employee leave requests and tracking leave balances efficiently.

## Features

### For Employees
- **Leave Request Management**
- Submit leave requests with date selection
- View leave balance for different leave types
- Track request status (Pending, Approved, Rejected)
- View leave history and upcoming leaves

### For Administrators
- **User Management**
- Create and manage user accounts
- Add additional admin users
- Set initial leave balances
- Manage departments

- **Leave Approval System**
- Review pending leave requests
- Approve or reject requests with comments
- Monitor leave balances before approval

- **Calendar View**
- Interactive calendar display
- Color-coded leave types
- Weekend and holiday highlights
- Monthly leave patterns

- **Analytics & Reports**
- Leave usage analysis
- Department-wise statistics
- Leave pattern visualization
- Monthly and yearly summaries

### System Features
- Secure login system
- Data backup functionality
- User-friendly interface
- Responsive design

## Leave Types
- Earned Leave (EL)
- Casual Leave (CL)
- Sick Leave (SL)
- Optional Holiday (OH)

## Technical Details
- Built with Python and Streamlit
- Data persistence using pickle files
- Interactive visualizations with Plotly
- Modular component-based architecture

## Getting Started

### Prerequisites
```python
streamlit
pandas
plotly
Installation
Clone the repository
git clone https://github.com/yourusername/leave-management-system.git
Install dependencies
pip install -r requirements.txt
Run the application
streamlit run app/main.py
Default Admin Credentials
Username: admin
Password: admin123


Security Features
Password hashing
Session management
Role-based access control
Contributing
Feel free to fork the repository and submit pull requests for any improvements.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
Built with Streamlit
Visualization powered by Plotly
Calendar implementation inspired by standard calendar views