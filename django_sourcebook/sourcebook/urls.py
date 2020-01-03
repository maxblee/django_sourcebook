from django.urls import path
from sourcebook.views import (
    index,
    create_foia_request,
)
urlpatterns = [
    path("", index, name="index"),
    path("foia-request/", create_foia_request, name="create_foia_request")
]