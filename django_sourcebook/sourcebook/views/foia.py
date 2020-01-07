from django.db.models import F
from sourcebook.models import FoiaRequestBase, FoiaRequestItem
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.views.generic import ListView


class FoiaRequestListView(ListView):
    model = FoiaRequestBase
    template_name = "foia/foia_request_list.html"
    paginate_by = 1

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query is None or query == "":
            return FoiaRequestBase.objects.all()
        search_query = SearchQuery(query)
        return (
            FoiaRequestBase.objects.filter(search_vector=search_query)
            .annotate(rank=SearchRank(F("search_vector"), query))
            .order_by("-rank")
        )

    def get_context_data(self, **kwargs):
        context = super(FoiaRequestListView, self).get_context_data(**kwargs)
        results = self.get_queryset()
        context["query"] = self.request.GET.get("q")
        context["count"] = results.count()
        context["count_requests"] = results.prefetch_related(
            "foiarequestitem_set"
        ).count()
        return context
