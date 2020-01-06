from django.urls import path
from sourcebook.views import (
    index,
)
from sourcebook.views.sourcebook import SourcesListView

urlpatterns = [
    path("", index, name="source_index"),
    path("sources/", SourcesListView.as_view(), name="source_list")
]