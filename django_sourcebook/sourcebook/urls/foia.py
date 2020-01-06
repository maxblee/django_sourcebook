from django.urls import path
from sourcebook import views

urlpatterns = [
    path("", views.foia_index, name="foia_index"),
    path("foia-request/", views.create_foia_request, name="create_foia_request")
]