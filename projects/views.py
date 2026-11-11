from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import Project


def home(request):
    return render(request, "projects/home.html")


def project_list(request):
    query = request.GET.get("q", "").strip()
    projects = Project.objects.select_related("department").order_by("-date_submitted")
    if query:
        projects = projects.filter(title__icontains=query)
    return render(
        request,
        "projects/project_list.html",
        {"projects": projects, "query": query},
    )


@login_required
def project_create(request):
    form = ProjectForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project submitted successfully.")
        return redirect("project_list")
    return render(
        request,
        "projects/project_form.html",
        {"form": form, "heading": "Add Project"},
    )


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(
        request.POST if request.method == "POST" else None,
        instance=project,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project updated successfully.")
        return redirect("project_list")
    return render(
        request,
        "projects/project_form.html",
        {"form": form, "heading": "Edit Project", "project": project},
    )


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect("project_list")
    return render(request, "projects/project_confirm_delete.html", {"project": project})