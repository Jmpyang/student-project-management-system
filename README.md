# Student Project Management System

A Django application for submitting and managing student projects by department.

## Setup

Run the following commands from the repository root:

```bash
python manage.py makemigrations projects
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sign in at `/accounts/login/` with the superuser credentials to add, edit, or
delete projects. Create departments in the Django admin at `/admin/` before
submitting projects. The project list is available at `/projects/`; its search
box filters project titles.

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