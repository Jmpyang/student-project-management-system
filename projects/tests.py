import re
from importlib import import_module
from types import SimpleNamespace

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.db import connection
from django.template.loader import render_to_string
from django.test import Client, TestCase
from django.urls import reverse

from .forms import ProjectForm
from .models import Department, Project


class ProjectManagementTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name="Computing",
            description="Computing department",
        )
        self.project = Project.objects.create(
            title="Library Portal",
            student_name="Amina Student",
            registration_number="CS001",
            description="A project description",
            department=self.department,
        )
        self.user = get_user_model().objects.create_user(
            username="student",
            password="test-password",
        )

    def test_home_and_project_list_render(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["welcome_message"],
            "Welcome to the Student Project Management System",
        )
        self.assertContains(
            response,
            "<h1>Welcome to the Student Project Management System</h1>",
        )
        self.assertContains(
            response,
            f'href="{reverse("home")}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("project_list")}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("project_create")}"',
        )

        response = self.client.get(reverse("project_list"))
        self.assertContains(response, "Library Portal")
        self.assertContains(response, "Amina Student")
        self.assertContains(response, "CS001")
        self.assertContains(response, "Computing")
        self.assertContains(response, 'href="/static/projects/css/style.css"')

    def test_navigation_links_open_their_named_pages(self):
        projects_response = self.client.get(reverse("project_list"))
        self.assertEqual(projects_response.status_code, 200)
        self.assertContains(projects_response, "Library Portal")

        self.client.force_login(self.user)
        add_project_response = self.client.get(reverse("project_create"))
        self.assertEqual(add_project_response.status_code, 200)
        self.assertContains(add_project_response, "Add Project")

    def test_home_template_extends_base_and_shows_welcome_message(self):
        rendered_template = render_to_string(
            "projects/home.html",
            {
                "welcome_message": (
                    "Welcome to the Student Project Management System"
                ),
            },
        )

        self.assertIn(
            "Welcome to the Student Project Management System",
            rendered_template,
        )
        self.assertIn('<nav class="site-nav"', rendered_template)

    def test_model_fields_match_assignment_requirements(self):
        self.assertEqual(Department._meta.get_field("name").max_length, 100)
        self.assertEqual(Project._meta.get_field("title").max_length, 200)
        self.assertEqual(Project._meta.get_field("student_name").max_length, 150)
        self.assertEqual(
            Project._meta.get_field("registration_number").max_length,
            30,
        )
        self.assertTrue(
            Project._meta.get_field("date_submitted").auto_now_add
        )
        self.assertIs(
            Project._meta.get_field("department").remote_field.model,
            Department,
        )

    def test_department_relationship_filters_projects(self):
        other_department = Department.objects.create(
            name="Engineering",
            description="Engineering department",
        )
        other_project = Project.objects.create(
            title="Bridge Design",
            student_name="Other Student",
            registration_number="EN001",
            description="A bridge design project",
            department=other_department,
        )

        self.assertEqual(
            list(Project.objects.filter(department=self.department)),
            [self.project],
        )
        self.assertEqual(other_project.department, other_department)

    def test_default_department_exists_once_and_migration_is_idempotent(self):
        default_name = "Information Technology"
        default_description = (
            "Department responsible for information technology projects "
            "and research."
        )
        self.assertEqual(
            Department.objects.filter(name=default_name).count(),
            1,
        )
        default_department = Department.objects.get(name=default_name)
        self.assertEqual(default_department.description, default_description)

        default_department.delete()
        existing_department = Department.objects.create(
            name=default_name,
            description="Existing department description",
        )
        migration = import_module(
            "projects.migrations.0002_default_department"
        )
        schema_editor = SimpleNamespace(connection=connection)
        migration.create_default_department(django_apps, schema_editor)
        migration.create_default_department(django_apps, schema_editor)

        self.assertEqual(
            Department.objects.filter(name=default_name).count(),
            1,
        )
        existing_department.refresh_from_db()
        self.assertEqual(
            existing_department.description,
            "Existing department description",
        )

    def test_project_form_requires_department_and_offers_default(self):
        default_department = Department.objects.get(
            name="Information Technology"
        )
        form = ProjectForm()

        self.assertTrue(form.fields["department"].required)
        self.assertIn(
            default_department,
            form.fields["department"].queryset,
        )
        self.assertFalse(
            ProjectForm(
                {
                    "title": "Missing Department",
                    "student_name": "Amina Student",
                    "registration_number": "CS005",
                    "description": "A project without a department",
                }
            ).is_valid()
        )

        self.client.login(username="student", password="test-password")
        response = self.client.post(
            reverse("project_create"),
            {
                "title": "IT Department Project",
                "student_name": "Amina Student",
                "registration_number": "IT001",
                "description": "Created using the default department",
                "department": default_department.pk,
            },
        )

        self.assertRedirects(response, reverse("project_list"))
        project = Project.objects.get(title="IT Department Project")
        self.assertEqual(project.department, default_department)

    def test_project_list_handles_empty_results(self):
        Project.objects.all().delete()

        response = self.client.get(reverse("project_list"))

        self.assertContains(response, "No projects found.")

    def test_search_filters_by_project_title(self):
        Project.objects.create(
            title="Campus Map",
            student_name="Other Student",
            registration_number="CS002",
            description="Another project",
            department=self.department,
        )

        response = self.client.get(reverse("project_list"), {"q": "library"})

        self.assertContains(response, "Library Portal")
        self.assertNotContains(response, "Campus Map")

    def test_project_changes_require_authentication(self):
        for url_name, kwargs in (
            ("project_create", {}),
            ("project_update", {"pk": self.project.pk}),
            ("project_delete", {"pk": self.project.pk}),
        ):
            response = self.client.get(reverse(url_name, kwargs=kwargs))
            self.assertRedirects(
                response,
                f"{reverse('login')}?next={reverse(url_name, kwargs=kwargs)}",
            )

        create_response = self.client.post(
            reverse("project_create"),
            {
                "title": "Unauthorized",
                "student_name": "Anonymous",
                "registration_number": "NO001",
                "description": "Should not be saved",
                "department": self.department.pk,
            },
        )
        update_response = self.client.post(
            reverse("project_update", kwargs={"pk": self.project.pk}),
            {"title": "Unauthorized"},
        )
        delete_response = self.client.post(
            reverse("project_delete", kwargs={"pk": self.project.pk}),
        )

        self.assertEqual(create_response.status_code, 302)
        self.assertEqual(update_response.status_code, 302)
        self.assertEqual(delete_response.status_code, 302)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Library Portal")

    def test_authenticated_user_can_create_edit_and_delete_project(self):
        self.client.login(username="student", password="test-password")
        create_url = reverse("project_create")
        project_data = {
            "title": "New Research",
            "student_name": "Amina Student",
            "registration_number": "CS003",
            "description": "Research summary",
            "department": self.department.pk,
        }

        response = self.client.post(create_url, project_data, follow=True)
        self.assertRedirects(response, reverse("project_list"))
        self.assertContains(response, "Project submitted successfully.")
        project = Project.objects.get(title="New Research")

        edit_data = {**project_data, "title": "Updated Research"}
        response = self.client.post(
            reverse("project_update", kwargs={"pk": project.pk}),
            edit_data,
            follow=True,
        )
        self.assertRedirects(response, reverse("project_list"))
        self.assertContains(response, "Project updated successfully.")
        project.refresh_from_db()
        self.assertEqual(project.title, "Updated Research")

        delete_url = reverse("project_delete", kwargs={"pk": project.pk})
        self.assertContains(self.client.get(delete_url), "Confirm project deletion")
        response = self.client.post(delete_url, follow=True)
        self.assertRedirects(response, reverse("project_list"))
        self.assertContains(response, "Project deleted successfully.")
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_login_and_logout_views(self):
        response = self.client.post(
            reverse("login"),
            {"username": "student", "password": "test-password"},
        )
        self.assertRedirects(response, reverse("project_list"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_admin_can_manage_departments_and_projects(self):
        admin_user = get_user_model().objects.create_superuser(
            username="administrator",
            password="admin-password",
        )
        admin_client = Client()
        admin_client.force_login(admin_user)

        department_add_url = reverse("admin:projects_department_add")
        response = admin_client.post(
            department_add_url,
            {
                "name": "Admin Department",
                "description": "Created through Django Admin",
                "_save": "Save",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Department")
        self.assertTrue(
            Department.objects.filter(name="Admin Department").exists()
        )
        department = Department.objects.get(name="Admin Department")
        department_change_url = reverse(
            "admin:projects_department_change",
            args=[department.pk],
        )
        self.assertEqual(
            admin_client.get(department_change_url).status_code,
            200,
        )
        response = admin_client.post(
            department_change_url,
            {
                "name": "Updated Admin Department",
                "description": "Updated through Django Admin",
                "_save": "Save",
            },
            follow=True,
        )
        self.assertContains(response, "Updated Admin Department")
        department.refresh_from_db()
        self.assertEqual(department.name, "Updated Admin Department")
        department_delete_url = reverse(
            "admin:projects_department_delete",
            args=[department.pk],
        )
        self.assertEqual(admin_client.get(department_delete_url).status_code, 200)
        admin_client.post(
            department_delete_url,
            {"post": "yes"},
            follow=True,
        )
        self.assertFalse(
            Department.objects.filter(pk=department.pk).exists()
        )

        project_add_url = reverse("admin:projects_project_add")
        response = admin_client.post(
            project_add_url,
            {
                "title": "Admin Project",
                "student_name": "Admin Student",
                "registration_number": "AD001",
                "description": "Created for admin management test",
                "department": self.department.pk,
                "_save": "Save",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Project")
        project = Project.objects.get(title="Admin Project")
        project_change_url = reverse(
            "admin:projects_project_change",
            args=[project.pk],
        )
        self.assertEqual(admin_client.get(project_change_url).status_code, 200)
        response = admin_client.post(
            project_change_url,
            {
                "title": "Updated Admin Project",
                "student_name": project.student_name,
                "registration_number": project.registration_number,
                "description": project.description,
                "department": project.department_id,
                "_save": "Save",
            },
            follow=True,
        )
        self.assertContains(response, "Updated Admin Project")
        project.refresh_from_db()
        self.assertEqual(project.title, "Updated Admin Project")
        project_delete_url = reverse(
            "admin:projects_project_delete",
            args=[project.pk],
        )
        self.assertEqual(admin_client.get(project_delete_url).status_code, 200)
        admin_client.post(
            project_delete_url,
            {"post": "yes"},
            follow=True,
        )
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_create_form_enforces_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.get(reverse("project_create"))
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

        project_data = {
            "title": "CSRF Protected Project",
            "student_name": "Amina Student",
            "registration_number": "CS004",
            "description": "CSRF validation test",
            "department": self.department.pk,
        }
        rejected_response = client.post(reverse("project_create"), project_data)
        self.assertEqual(rejected_response.status_code, 403)

        token = re.search(
            rb'name="csrfmiddlewaretoken" value="([^"]+)"',
            response.content,
        )
        self.assertIsNotNone(token)
        accepted_response = client.post(
            reverse("project_create"),
            {**project_data, "csrfmiddlewaretoken": token.group(1).decode()},
        )
        self.assertRedirects(accepted_response, reverse("project_list"))
        self.assertTrue(
            Project.objects.filter(title="CSRF Protected Project").exists()
        )

    def test_invalid_project_submission_shows_validation_errors(self):
        self.client.login(username="student", password="test-password")

        response = self.client.post(reverse("project_create"), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Project.objects.count(), 1)
