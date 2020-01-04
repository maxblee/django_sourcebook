from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from sourcebook.models import FoiaStatus, FoiaRequestItem
from sourcebook.forms import FoiaRequestBaseForm, FoiaRequestFormSet
from sourcebook import foia_sender
# Create your views here.

def index(request):
    """The home page of our lovely source book!"""
    return render(
        request,
        "index.html",
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
        "sourcebook/foia_request.html",
        context=context
    )
