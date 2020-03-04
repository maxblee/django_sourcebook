import django
from django.db.models import F, Q
from sourcebook.models import FoiaRequestBase, FoiaRequestItem, Document, FoiaStatus
from django.shortcuts import render
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.views.generic import DetailView, ListView
from django.utils import timezone
import datetime


class FoiaRequestItemListView(ListView):
    model = FoiaRequestItem
    template_name = "foia/foia_request_item_list.html"
    paginate_by = 10

    def get_queryset(self):
        query_results = FoiaRequestItem.objects.select_related(
            "agency", "agency__state", "request_content"
        )
        status = self.request.GET.getlist("status")
        if status != []:
            query_results = query_results.filter(status__in=status)
        related_project = self.request.GET.get("related_project")
        if related_project is not None and related_project != "":
            query_results = query_results.filter(
                request_content__related_project__id=related_project
            )
        state = self.request.GET.get("state")
        if state is not None and state != "":
            query_results = query_results.filter(agency__state=state)
        # NOTE: This needs to be last (because we're shifting from a queryset to a list)
        if self.request.GET.get("overdue") == "on":
            query_results = self.get_overdue_requests(query_results)
        return query_results

    def get_overdue_requests(self, queryset):
        today = timezone.now().date()
        query_results = []
        for pr_request in queryset.filter(status=FoiaStatus.NO_RESPONSE):
            if pr_request.due_date is not None:
                # if it's a date
                if not isinstance(pr_request.due_date, datetime.datetime):
                    if pr_request.due_date < today:
                        query_results.append(pr_request)
                else:
                    if pr_request.due_date.date() < today:
                        query_results.append(pr_request)
        return query_results

    def get_context_data(self, **kwargs):
        context = super(FoiaRequestItemListView, self).get_context_data(**kwargs)
        results = self.get_queryset()
        if isinstance(results, django.db.models.query.QuerySet):
            context["count"] = results.count()
        else:
            context["count"] = len(results)
        return context

    def filter_late(self, queryset):
        return queryset


class FoiaRequestListView(ListView):
    model = FoiaRequestBase
    template_name = "foia/foia_request_list.html"
    paginate_by = 10

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
        context["count_requests"] = results.prefetch_related("foiarequests").count()
        return context


# Document Handling


def document_index(request):
    return render(request, "foia/documents/index.html")


class DocumentDetailView(DetailView):
    model = Document
    template_name = "foia/documents/document_detail.html"


class FoiaRequestDetail(DetailView):
    model = FoiaRequestItem
    template_name = "foia/request_detail.html"
