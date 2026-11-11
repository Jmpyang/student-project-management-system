from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

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
        self.assertContains(self.client.get(reverse("home")), "Welcome")

        response = self.client.get(reverse("project_list"))
        self.assertContains(response, "Library Portal")
        self.assertContains(response, "Amina Student")
        self.assertContains(response, "CS001")
        self.assertContains(response, "Computing")

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

        response = self.client.post(create_url, project_data)
        self.assertRedirects(response, reverse("project_list"))
        project = Project.objects.get(title="New Research")

        edit_data = {**project_data, "title": "Updated Research"}
        response = self.client.post(
            reverse("project_update", kwargs={"pk": project.pk}),
            edit_data,
        )
        self.assertRedirects(response, reverse("project_list"))
        project.refresh_from_db()
        self.assertEqual(project.title, "Updated Research")

        delete_url = reverse("project_delete", kwargs={"pk": project.pk})
        self.assertContains(self.client.get(delete_url), "Confirm project deletion")
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("project_list"))
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_invalid_project_submission_shows_validation_errors(self):
        self.client.login(username="student", password="test-password")

        response = self.client.post(reverse("project_create"), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Project.objects.count(), 1)
