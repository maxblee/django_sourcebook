from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchRank
from sourcebook.models import Source

SOURCE_TYPES = dict(Source.SourceType.choices)

class SourcesListView(ListView):
    model = Source
    template_name = "sourcebook/sources.html"
    fields = ("first_name", "last_name", "title", "entity",)
    paginate_by = 5

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query is None:
            return Source.objects.all()
        search_vector = SearchVector("last_name", "first_name", weight="A") + SearchVector("entity", weight="B") + SearchVector("title", weight="B")
        return Source.objects.annotate(rank=SearchRank(search_vector, query)).filter(rank__gte=0.3).order_by("rank")

    def get_context_data(self, **kwargs):
        context = super(SourcesListView, self).get_context_data(**kwargs)
        context["fields"] = [self.model._meta.get_field(field).verbose_name.title() for field in self.fields]
        context["count"] = self.get_queryset().count()
        context["query"] = self.request.GET.get("q")
        return context