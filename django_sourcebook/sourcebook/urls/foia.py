from django.urls import path
from sourcebook import views
from sourcebook.views.foia import FoiaRequestListView

urlpatterns = [
    path("", views.foia_index, name="foia_index"),
    path("foia-request/", views.create_foia_request, name="create_foia_request"),
    path("foia-request-list/", FoiaRequestListView.as_view(), name="foia_request_list"),
]
