# Class Plus Assistant

Class Plus Assistant is a desktop-based college management and academic assistant application built with Python and CustomTkinter. The system helps admins and students manage academic operations, lecture content, quiz activity, notes, and user profiles from a single interface.

## Overview

This project is designed for a college environment where:

- Admins can manage faculty, students, departments, courses, lectures, and quiz activity.
- Students can log in to view their dashboard, access courses, view lectures, and attempt quizzes.
- AI-based features help with lecture notes review and academic support.
- All major screens are designed for a full-screen desktop experience.

## Key Features

### Admin Features
- Admin login and role-based access
- Add and manage faculty members
- Add and manage students
- Add and manage departments
- Add and manage courses
- Add and review lectures
- View lecture questions
- Review AI-generated notes
- View quiz activity
- Edit profile and change password

### Student Features
- Student login
- Student dashboard
- View enrolled courses
- Access lectures
- Attempt quizzes
- View quiz history
- Edit profile and change password

### Additional Features
- Modern dark-themed GUI
- Full-screen desktop layout for core screens
- Database-backed data storage using MySQL
- Scrollable tables for data management
- Student status tracking (Active / Inactive)

## Tech Stack

- Python 3
- CustomTkinter for modern UI
- MySQL / PyMySQL for database connectivity
- Tkinter-based desktop application design

## Project Structure

```text
class_assistant_extracted/
├── README.md
├── Class_Assistant/
│   ├── main_navigator.py         # Main portal landing screen
│   ├── admin_login.py            # Admin login screen
│   ├── user_login.py             # Student login screen
│   ├── adminDashboard.py         # Admin dashboard
│   ├── user_dashboard.py         # Student dashboard
│   ├── add_admin.py              # Add faculty
│   ├── manage_admin.py           # Manage faculty
│   ├── add_user.py               # Add student
│   ├── manage_user.py            # Manage students
│   ├── add_dept.py               # Add department
│   ├── manage_dept.py            # Manage department
│   ├── add_courses.py            # Add course
│   ├── manage_courses.py         # Manage courses
│   ├── add_lecture.py            # Add lecture
│   ├── viewlecture.py            # View lectures
│   ├── viewquestions.py          # View questions
│   ├── veiwnotes.py              # Review AI notes
│   ├── veiwquizadmin.py          # Quiz activity view
│   ├── connection.py             # MySQL database connection
│   ├── edit_profile.py           # Edit profile
│   ├── change_pass.py            # Change password
│   ├── question_generator.py     # Question generation utilities
│   ├── notes_generator.py        # Notes generation utilities
│   ├── ai_pipeline.py            # AI processing flow
│   └── ...
└── venv/
```

## Database Setup

This application uses a MySQL database named `class_assistant`.

The connection settings are configured in `Class_Assistant/connection.py`:

```python
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    port=3306,
    password='system',
    database='class_assistant'
)
```

### MySQL Setup
1. Start MySQL on your machine.
2. Create the database:
   ```sql
   CREATE DATABASE class_assistant;
   ```
3. Make sure the tables used by the app exist for admin, student, courses, lectures, quizzes, and related data.
4. If needed, modify the database credentials in `connection.py` to match your local MySQL setup.

## Installation

### 1. Clone the project
```bash
git clone <your-repository-url>
cd class_assistant_extracted
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install customtkinter pymysql
```

## Run the Application

From the project folder:

```bash
cd Class_Assistant
python main_navigator.py
```

This opens the main portal screen where the user can choose:
- Teacher / HOD Login
- Student Login
- New Registration
- Exit

## How It Works

1. The application starts from `main_navigator.py`.
2. The user chooses Admin Login, Student Login, or Registration.
3. Relevant dashboard screens load based on the user role.
4. Admins can manage college data while students can access academic features.
5. Database records are used for login, profile management, course details, and quiz data.

## Under Development / Known Issues

This project is currently under active development and should be treated as a prototype / academic project rather than a production-ready application.

Possible issues that may occur include:

- Minor UI glitches or spacing inconsistencies on some screens
- Window transitions or dialog behavior depending on machine resolution and OS scaling
- Database connection issues if MySQL credentials or schema differ from local setup
- Incomplete validation in some forms or edge-case user inputs
- Some modules may still require bug fixing, optimization, or better error handling
- AI-generated features may behave inconsistently depending on data quality and environment setup

This project is useful for learning, demo purposes, and college-level academic implementation, but it may still contain bugs, incomplete logic, or areas needing improvement.

## Notes

- This project is designed for local desktop use and uses a local MySQL database.
- Some modules may require database tables to be created and populated before full use.
- The codebase includes AI-related functions for notes and quiz support.
- Features are still being refined and may change over time.

## License

This project is currently for educational / academic use.

## Author

Developed as a college assistant and academic management system.

## Future Improvements

- Add role-based permissions more strictly
- Improve AI note and question generation
- Add export/report generation
- Improve validation and error handling
- Add password hashing for better security
