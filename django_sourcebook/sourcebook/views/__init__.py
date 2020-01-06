import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, ExpressionWrapper, fields, Avg, Min, Max, Count, Sum
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from sourcebook.models import (
    FoiaStatus, 
    FoiaRequestItem,
    Source,
    Story
)
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
    num_cur_yr = FoiaRequestItem.objects.filter(request_content__date_filed__year=current_year).count()
    # https://stackoverflow.com/questions/3131107/annotate-a-queryset-with-the-average-date-difference-django
    duration = ExpressionWrapper(F("time_completed") - F("request_content__date_filed"), output_field=fields.DurationField())
    resp_time_data = FoiaRequestItem.objects.exclude(
        time_completed=None
        ).annotate(duration=duration).aggregate(Avg("duration"), Max("duration"), Min("duration"))
    context = {
        "num_requests": num_foia_requests,
        "num_cur_yr": num_cur_yr,
        "avg_resp_time": resp_time_data["duration__avg"].days,
        "max_resp_time": resp_time_data["duration__max"].days,
        "min_resp_time": resp_time_data["duration__min"].days
    }
    return render(request, "foia/index.html", context)

def index(request):
    """The home page of our lovely source book!"""
    # the number of new sources you added this past week
    new_sources = Source.objects.filter(time_added__gte=timezone.now() - datetime.timedelta(days=7)).count()
    total_sources = Source.objects.all().count()
    # basic statistics about the usage of sources in stories
    story_sources = Story.objects.all().annotate(num_sources=Count("sources")).aggregate(
        Avg("num_sources"),
        Max("num_sources"),
        Min("num_sources")
        )
    # gender and race statistics
    # total number of men, women, etc among sources
    overall_gender = Source.objects.values("gender").annotate(count=Count("gender")).distinct().order_by()
    num_women, num_men, num_nonbin = (
        get_object_or_default(overall_gender, default={"count":0}, gender='w')["count"],
        get_object_or_default(overall_gender, default={"count":0}, gender='m')["count"],
        get_object_or_default(overall_gender, default={"count":0}, gender='n')["count"]
    )
    pct_men_overall = num_men / (num_women + num_men + num_nonbin)
    overall_race = Source.objects.values("race").annotate(count=Count("race")).distinct().order_by()
    num_poc, num_white = (
        get_object_or_default(overall_race, default={"count":0}, race='poc')["count"],
        get_object_or_default(overall_race, default={"count":0}, race='w')["count"]
    )
    pct_white_overall = num_white / (num_poc + num_white)
    story_gender = Story.objects.values("sources__gender").annotate(
        num_women=Count("id", filter=Q(sources__gender='w')),
        num_men=Count("id", filter=Q(sources__gender='m')),
        num_nonbin=Count("id", filter=Q(sources__gender='n'))
    ).aggregate(
        total_women=Sum("num_women"),
        total_men=Sum("num_men"),
        total_nonbin=Sum("num_nonbin")
    )
    pct_men_story = story_gender["total_men"] / (story_gender["total_men"] + story_gender["total_women"] + story_gender["total_nonbin"])
    story_race = Story.objects.values("sources__race").annotate(
        num_white=Count("id", filter=Q(sources__race='w')),
        num_poc=Count("id", filter=Q(sources__race='poc'))
    ).aggregate(
        total_white=Sum("num_white"),
        total_poc=Sum("num_poc")
    )
    pct_white_story = story_race["total_white"] / (story_race["total_white"] + story_race["total_poc"])
    context = {
        "new_sources":new_sources,
        "total_sources":total_sources,
        "pct_men_overall": f"{pct_men_overall * 100:0.0f}",
        "pct_white_overall": f"{pct_white_overall * 100:0.0f}",
        "pct_men_story": f"{pct_men_story * 100:0.0f}",
        "pct_white_story": f"{pct_white_story * 100:0.0f}"
    }
    return render(
        request,
        "sourcebook/index.html",
        context
    )

def create_foia_request(request):
    if request.method == "POST":
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
                foia_email = foia_sender.FoiaHandler(foia_request, current_foia)
                foia_email.file_request()
            return HttpResponseRedirect(reverse("index"))
    else:
        base_request = FoiaRequestBaseForm()
        agency_requests = FoiaRequestFormSet(queryset=FoiaRequestItem.objects.none())
    context = {
        "foia_base": base_request,
        "foia_formset": agency_requests
    }
    return render(
        request,
        "foia/foia_request.html",
        context=context
    )