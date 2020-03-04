from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.db.models import Q, F
from sourcebook.models import Source

SOURCE_TYPES = dict(Source.SourceType.choices)


class SourcesListView(ListView):
    model = Source
    template_name = "sourcebook/sources.html"
    fields = (
        "first_name",
        "last_name",
        "title",
        "entity",
    )
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query is None or query == "":
            return Source.objects.all()
        search_query = SearchQuery(query)
        # combining searches from http://rubyjacket.com/build/django-psql-fts.html
        return (
            Source.objects.filter(
                Q(search_vector=search_query) | Q(entity__search_vector=search_query)
            )
            .annotate(source_rank=SearchRank(F("search_vector"), search_query))
            .annotate(entity_rank=SearchRank(F("entity__search_vector"), search_query))
            .annotate(rank=F("source_rank") + F("entity_rank"))
            .order_by("-rank", "last_name", "first_name")
        )

    def get_context_data(self, **kwargs):
        context = super(SourcesListView, self).get_context_data(**kwargs)
        context["fields"] = [
            self.model._meta.get_field(field).verbose_name.title()
            for field in self.fields
        ]
        context["count"] = self.get_queryset().count()
        context["query"] = self.request.GET.get("q")
        return context
