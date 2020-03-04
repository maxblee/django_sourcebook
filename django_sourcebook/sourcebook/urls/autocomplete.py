from django.urls import path
from django.conf.urls import url
from sourcebook.views.autocomplete import (
    SourceAutocomplete,
    EntityAutocomplete,
    SourceMatchesEntity,
)

urlpatterns = [
    url(
        r"^source-autocomplete/$",
        SourceAutocomplete.as_view(),
        name="source-autocomplete",
    ),
    path(
        "entity-autocomplete/", EntityAutocomplete.as_view(), name="entity-autocomplete"
    ),
    path(
        "source-match-entity/",
        SourceMatchesEntity.as_view(),
        name="source-match-entity",
    ),
]
