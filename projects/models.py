from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200)
    student_name = models.CharField(max_length=150)
    registration_number = models.CharField(max_length=30)
    description = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    def __str__(self):
        return self.title
