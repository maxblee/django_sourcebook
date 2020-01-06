from django.urls import path
from sourcebook import views

urlpatterns = [
    path("", views.projects_index, name="project_index")
]