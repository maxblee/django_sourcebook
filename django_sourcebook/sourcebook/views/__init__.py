import datetime
from django.contrib import messages 
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, ExpressionWrapper, fields, Avg, Min, Max, Count, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from sourcebook.models import FoiaStatus, FoiaRequestItem, Source, Story
from sourcebook.forms import FoiaRequestBaseForm, FoiaRequestFormSet
from sourcebook import foia_sender

# Create your views here.

# modified from https://github.com/skorokithakis/django-annoying/blob/master/annoying/functions.py
# to add default
def get_object_or_default(klass, default=None, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.
    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.
    Note: Like with get(), a MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    from django.shortcuts import _get_queryset

    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return default


def site_index(request):
    """The home page for our entire site!!!"""
    return render(request, "index.html")


def projects_index(request):
    """The home page for our projects"""
    return render(request, "projects/index.html")


def foia_index(request):
    """The home page for the FOIA app"""
    current_year = timezone.now().date().year
    num_foia_requests = FoiaRequestItem.objects.all().count()
    num_cur_yr = FoiaRequestItem.objects.filter(
        request_content__date_filed__year=current_year
    ).count()
    # https://stackoverflow.com/questions/3131107/annotate-a-queryset-with-the-average-date-difference-django
    duration = ExpressionWrapper(
        F("time_completed") - F("request_content__date_filed"),
        output_field=fields.DurationField(),
    )
    resp_time_data = (
        FoiaRequestItem.objects.exclude(time_completed=None)
        .annotate(duration=duration)
        .aggregate(Avg("duration"), Max("duration"), Min("duration"))
    )
    context = {
        "num_requests": num_foia_requests,
        "num_cur_yr": num_cur_yr,
        "avg_resp_time": resp_time_data["duration__avg"].days if resp_time_data["duration__avg"] is not None else None,
        "max_resp_time": resp_time_data["duration__max"].days if resp_time_data["duration__max"] is not None else None,
        "min_resp_time": resp_time_data["duration__min"].days if resp_time_data["duration__min"] is not None else None,
    }
    return render(request, "foia/index.html", context)

def _safe_division(numerator, denominator):
    """Returns none if you'd get a ZeroDivisionError else divides"""
    if denominator == 0:
        return None
    return numerator / denominator

def index(request):
    """The home page of our lovely source book!"""
    # the number of new sources you added this past week
    new_sources = Source.objects.filter(
        time_added__gte=timezone.now() - datetime.timedelta(days=7)
    ).count()
    total_sources = Source.objects.all().count()
    # basic statistics about the usage of sources in stories
    story_sources = (
        Story.objects.all()
        .annotate(num_sources=Count("sources"))
        .aggregate(Avg("num_sources"), Max("num_sources"), Min("num_sources"))
    )
    # gender and race statistics
    # total number of men, women, etc among sources
    overall_gender = (
        Source.objects.values("gender")
        .annotate(count=Count("gender"))
        .distinct()
        .order_by()
    )
    num_women, num_men, num_nonbin = (
        get_object_or_default(overall_gender, default={"count": 0}, gender="w")[
            "count"
        ],
        get_object_or_default(overall_gender, default={"count": 0}, gender="m")[
            "count"
        ],
        get_object_or_default(overall_gender, default={"count": 0}, gender="n")[
            "count"
        ],
    )

    pct_men_overall = _safe_division(num_men, num_men + num_women + num_nonbin)
    overall_race = (
        Source.objects.values("race")
        .annotate(count=Count("race"))
        .distinct()
        .order_by()
    )
    num_poc, num_white = (
        get_object_or_default(overall_race, default={"count": 0}, race="poc")["count"],
        get_object_or_default(overall_race, default={"count": 0}, race="w")["count"],
    )
    pct_white_overall = _safe_division(num_white, num_poc + num_white) 
    story_gender = (
        Story.objects.values("sources__gender")
        .annotate(
            num_women=Count("id", filter=Q(sources__gender="w")),
            num_men=Count("id", filter=Q(sources__gender="m")),
            num_nonbin=Count("id", filter=Q(sources__gender="n")),
        )
        .aggregate(
            total_women=Coalesce(Sum("num_women"), Value(0)),
            total_men= Coalesce(Sum("num_men"), Value(0)),
            total_nonbin= Coalesce(Sum("num_nonbin"), Value(0))
        )
    )
    pct_men_story = _safe_division(
        story_gender["total_men"],
        story_gender["total_women"] + story_gender["total_nonbin"] + story_gender["total_men"]
    )

    story_race = (
        Story.objects.values("sources__race")
        .annotate(
            num_white=Count("id", filter=Q(sources__race="w")),
            num_poc=Count("id", filter=Q(sources__race="poc")),
        )
        .aggregate(
            total_white= Coalesce(Sum("num_white"), Value(0)), 
            total_poc= Coalesce(Sum("num_poc"), Value(0))
            )
    )
    pct_white_story = _safe_division(
        story_race["total_white"], 
        story_race["total_white"] + story_race["total_poc"]
    )

    context = {
        "new_sources": new_sources,
        "total_sources": total_sources,
        "pct_men_overall": f"{pct_men_overall * 100:0.0f}" if pct_men_overall is not None else "",
        "pct_white_overall": f"{pct_white_overall * 100:0.0f}" if pct_white_overall is not None else "",
        "pct_men_story": f"{pct_men_story * 100:0.0f}" if pct_men_story is not None else None,
        "pct_white_story": f"{pct_white_story * 100:0.0f}" if pct_white_story is not None else None,
    }
    return render(request, "sourcebook/index.html", context)


def create_foia_request(request):
    if request.method == "POST":
        params = {}
        if "cc" in request.POST:
            params["cc"] = request.POST["cc"]
        if "bcc" in request.POST:
            params["bcc"] = request.POST["bcc"]
        base_request = FoiaRequestBaseForm(request.POST)
        agency_requests = FoiaRequestFormSet(request.POST)
        if base_request.is_valid() and agency_requests.is_valid():
            foia_request = base_request.save(commit=False)
            foia_request.date_filed = timezone.now()
            foia_request.save()
            for form in agency_requests:
                current_foia = form.save(commit=False)
                current_foia.request_content = foia_request
                current_foia.status = FoiaStatus.NO_RESPONSE
                current_foia.expedited_processing_granted = False
                current_foia.save()
                try:
                    foia_email = foia_sender.FoiaHandler(foia_request, current_foia, **params)
                    foia_email.file_request()
                except foia_sender.FoiaTemplateError:
                    messages.error(request, "You must add a valid template for this entity")
                    return HttpResponseRedirect(reverse("create_foia_request"))
            return HttpResponseRedirect(reverse("foia_index"))
    else:
        base_request = FoiaRequestBaseForm()
        agency_requests = FoiaRequestFormSet(queryset=FoiaRequestItem.objects.none())
    context = {"foia_base": base_request, "foia_formset": agency_requests}
    return render(request, "foia/foia_request.html", context=context)
