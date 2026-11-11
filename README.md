# Student Project Management System

A Django application for submitting and managing student projects by department.

## Setup

Run the following commands from the repository root:

```bash
source venv/bin/activate
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sign in at `/accounts/login/` with the superuser credentials to add, edit, or
delete projects. The migration creates the Information Technology department
if it does not already exist. Manage departments and projects in Django Admin
at `/admin/`. The project form requires a department selection. The project
list is available at `/projects/`; its search box filters project titles.

To create an ordinary test user, open the Django shell and use Django's
built-in user model:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
get_user_model().objects.create_user(
    username="student",
    password="replace-with-a-private-password",
)
```

Alternatively, an administrator can create a regular user in Django Admin's
Users section. No custom user model is used.

## Models and ORM query

`Department` stores a name and description. Each `Project` stores its title,
student details, description, submission timestamp, and a foreign key to a
department. Retrieve projects for one department with:

```python
Project.objects.filter(department=department)
```

The project list uses `select_related("department")` to load each related
department efficiently.

## Tests

Run the application checks and tests with:

```bash
python manage.py check
python manage.py test projects
```