# Your Space

## Overview
Your Space is a comprehensive space and subscription management web application built with Flask. It provides tools for managing users, institutes, customers, jobs, logs, packages, pricing rules, spaces, and subscriptions. The app features an admin dashboard, user authentication, and detailed CRUD operations for all entities.

## Features
- **User Authentication**: Login/logout, password change, admin/user roles.
- **Admin Dashboard**: Overview of system status and quick access to all modules.
- **User Management**: Add, edit, delete, and list users. Admin role assignment.
- **Institute Management**: Add, edit, delete, and list institutes.
- **Customer Management**: Add, edit, delete, and list customers. External customer support.
- **Job Management**: Add, edit, delete, and list jobs.
- **Log Management**: Add, edit, delete, and list logs. View logs by customer.
- **Package Management**: Add, edit, delete, and list packages. View package details.
- **Pricing Rules**: Add, edit, delete, and list pricing rules.
- **Space Management**: Add, edit, delete, and list spaces.
- **Subscription Management**: Add, edit, delete, and list subscriptions. View subscription details.
- **Export to Excel**: Export data for any model to Excel.
- **Responsive UI**: Modern, mobile-friendly interface with custom styles and images.

## Screens
- **Login**: User authentication screen (username & password).
- **Dashboard**: Admin overview with quick links.
- **Users**: List, add, edit, delete users.
- **Institutes**: List, add, edit, delete institutes.
- **Customers**: List, add, edit, delete customers (internal/external).
- **Jobs**: List, add, edit, delete jobs.
- **Logs**: List, add, edit, delete logs. View by customer.
- **Packages**: List, add, edit, delete packages. View details.
- **Pricing Rules**: List, add, edit, delete pricing rules.
- **Spaces**: List, add, edit, delete spaces.
- **Subscriptions**: List, add, edit, delete subscriptions. View details.
- **Change Password**: User password management.
- **About**: App information and credits.

## Default Admin Credentials
- **Username**: `admin2`
- **Password**: `admin2`

## Setup & Usage
1. Install dependencies: `pip install -r requirements.txt` or use Poetry.
2. Run the app: `python main.py`
3. Access via browser at `http://localhost:5000`.

## File Structure
- `main.py`: App entry point.
- `app/`: Main application package.
  - `routes.py`: All route handlers.
  - `models.py`: Database models.
  - `forms.py`: WTForms definitions.
  - `templates/`: Jinja2 HTML templates.
  - `static/`: CSS, JS, images, fonts.
- `migrations/`: Alembic migration scripts.

## Notes
- Login uses **username** (not email) and password.
- All CRUD screens are accessible from the dashboard.
- Admin can manage all entities; regular users have limited access.

---
For more details, see code comments and explore the UI.
