# Student Project Management System

A Django web application for submitting, viewing, searching, updating, and managing student projects by department.

## 1. Technologies Used

- Python 3.14
- Django 6.1.3
- SQLite
- HTML5
- CSS3
- Django Authentication System
- Django Admin

## 2. Project Features

### Public Features
- View all submitted student projects.
- Search for projects by title.
- View project information, including student name, registration number, description, and department.

### Authenticated User Features

Users who are logged in can:
- Submit new student projects.
- Update existing projects.
- Delete projects after confirmation.

### Administrator Features

Django Admin provides authorized administrators with the ability to:
- Manage departments.
- Manage student projects.
- Manage user accounts.

**Note:** All authenticated users can create, update, and delete projects. The application does not implement separate project-management roles.

## 3. Project Structure

```text
student-project-management-system/
│
├── StudentProjectSystem/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── projects/
│   ├── migrations/
│   ├── static/
│   │   └── projects/
│   │       └── css/
│   │           └── style.css
│   ├── templates/
│   │   └── projects/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .gitignore
├── LICENSE
├── manage.py
├── README.md
└── requirements.txt
```

## 4. Installation and Setup

### Prerequisites

- Python 3.14 or a compatible Python version.
- Git.
- A terminal such as Windows PowerShell or Command Prompt.

### Step 1: Clone the repository

```bash
git clone https://github.com/Jmpyang/student-project-management-system.git
```

Navigate into the project directory:

```bash
cd student-project-management-system
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

### Step 3: Activate the virtual environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
venv\Scripts\activate.bat
```

For Linux or macOS:

```bash
source venv/bin/activate
```

### Step 4: Install project dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 5: Apply database migrations

```bash
python manage.py migrate
```

This creates the required database tables.

The project migration also creates the default Information Technology department if it does not already exist.

### Step 6: Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the prompts to create your administrator username and password.

### Step 7: Run the development server

```bash
python manage.py runserver
```

Open the application in your browser:

**Home page:**

http://127.0.0.1:8000/

## 5. Application URLs

| URL | Description | Access |
|---|---|---|
| `/` | Home page | Public |
| `/projects/` | View and search projects | Public |
| `/projects/add/` | Submit a new project | Login required |
| `/projects/<id>/edit/` | Update an existing project | Login required |
| `/projects/<id>/delete/` | Delete a project | Login required |
| `/accounts/login/` | User login | Public |
| `/accounts/logout/` | User logout | Login required |
| `/admin/` | Django administration | Staff access required |

## 6. Database Models

The application uses two main database models.

### Department

Stores department information:

- `name`: Department name.
- `description`: Department description.

### Project

Stores student project information:

- `title`: Project title.
- `student_name`: Name of the student.
- `registration_number`: Student registration number.
- `description`: Project description.
- `date_submitted`: Automatically recorded submission date and time.
- `department`: Foreign key relationship to the Department model.

Each project belongs to a department. The relationship uses Django's `ForeignKey` field with cascading deletion.

## 7. Authentication and Authorization

The application uses Django's built-in authentication system.

- Anonymous visitors can view and search submitted projects.
- Users must authenticate before creating, updating, or deleting projects.
- Authorized staff users can access Django Admin.
- The application uses Django's default user model.
- No custom user model has been implemented.

Administrators can create ordinary user accounts through the Users section of Django Admin.

## 8. Searching Projects

The project list includes a search form that filters projects by title.

The search uses Django ORM's case-insensitive `icontains` lookup.

Example:

```python
Project.objects.filter(title__icontains="management")
```

The project list also uses:

```python
select_related("department")
```

This retrieves related department information efficiently when displaying projects.

## 9. Static Files

The application stylesheet is located at:

```text
projects/static/projects/css/style.css
```

The stylesheet is referenced by the base template and is served by Django during local development.

## 10. Testing

The project includes automated tests covering important application functionality.

Run Django system checks:

```bash
python manage.py check
```

Run all automated tests:

```bash
python manage.py test
```

The test suite covers:

- Department and Project models.
- Model relationships and field constraints.
- Project forms and validation.
- Project creation, updating, and deletion.
- Project listing and title searching.
- Authentication and authorization.
- Login and logout.
- Django Admin functionality.
- Database migrations and default department creation.
- CSRF protection.

## 11. Development Notes

- SQLite is used as the development database.
- Database tables are managed through Django migrations.
- The Information Technology department is created through the project's database migration.
- The local SQLite database is excluded from Git tracking. A fresh database is created when migrations are applied.
- Python cache files and virtual environments are excluded through `.gitignore`.
- The included Django settings are intended for local development and academic assessment, not production deployment.
- No default username or password is provided. Users must create their own accounts.

## 12. Repository

GitHub Repository:

https://github.com/Jmpyang/student-project-management-system