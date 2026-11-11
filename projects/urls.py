from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_update, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('accounts/login/', LoginView.as_view(template_name='projects/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
]