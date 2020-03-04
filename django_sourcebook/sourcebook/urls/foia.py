from django.urls import path
from sourcebook import views
from sourcebook.views.foia import (
    FoiaRequestDetail,
    FoiaRequestListView,
    FoiaRequestItemListView,
    document_index,
    DocumentDetailView,
)

urlpatterns = [
    path("", views.foia_index, name="foia_index"),
    path("request-<int:pk>/", FoiaRequestDetail.as_view(), name="foia_request_detail"),
    path("browse/", FoiaRequestItemListView.as_view(), name="foia_browse"),
    path("foia-request/", views.create_foia_request, name="create_foia_request"),
    path("search/", FoiaRequestListView.as_view(), name="foia_request_list"),
    path("documents/", document_index, name="document_index"),
    path("documents/<int:pk>", DocumentDetailView.as_view(), name="document_detail"),
]
