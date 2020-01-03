from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import us
from phonenumber_field.modelfields import PhoneNumberField
from taggit.managers import TaggableManager
from django_better_admin_arrayfield.models.fields import ArrayField
import reversion
import datetime
# import top-level package utilities
import sys
sys.path.append("..")
import utils.validators
# Create your models here.
RCFP_BASE_URL = "https://www.rcfp.org/open-government-guide/"

class FoiaStatus(models.TextChoices):
    NO_RESPONSE = "nr", _("no response")
    ACKNOWLEDGED = "a", _("acknowledged")
    CLOSED_FULFILLED = "cf", _("closed - no redactions")
    CLOSED_REDACTED = "cr", _("closed - some redactions")
    CLOSED_EXCESS_FEE = "ce", _("closed - did not pay fee")
    APPEALED = "ap", _("appealed")
    SUED = "s", _("sued")

def get_current_date():
    return timezone.now().date()

@reversion.register(fields=["foia_template"])
class State(models.Model):
    fips_code = models.CharField(max_length=2, validators=[utils.validators.validate_fips])
    public_records_act_name = models.CharField("name of state public records act", max_length=200, blank=True, null=True)
    foia_template = models.FileField(
        upload_to="foia_templates/", 
        verbose_name="Public Records act template",
        validators=[utils.validators.validate_template_extension],
        blank=True,
        null=True
    )
    # most states have a maximum response time allowed for agencies to respond to public records requests
    # but some do not :(
    maximum_response_time = models.PositiveSmallIntegerField(
        help_text="What is the maximum response time allowed under this state's public records act?",
        blank=True,
        null=True
    )
    # states differ in whether the response time refers to business days or total days
    business_days = models.BooleanField(
        blank=True,
        null=True,
        help_text="Is the response time the number of business days or actual days to respond to requests?"
    )

    def __str__(self):
        return self.info.name

    @property
    def info(self):
        """Gets basic information for the state, directly from the `python-us` package."""
        # there's no need to run error handling here because that's handled in validation
        return us.states.lookup(self.fips_code)

    @property
    def foia_guide(self):
        """Returns the Reporter's Committee for the Freedom of the Press Open Government Guide for the given state.
        
        That guide only applies to states and D.C. (not territories), so we'll return `None` for territories.
        """
        if self.info.is_territory:
            return None
        state_cleaned = "-".join(self.info.name.lower().split())
        return RCFP_BASE_URL + state_cleaned + "/"

    class Meta:
        ordering = ["fips_code"]


class Entity(models.Model):
    name = models.CharField(max_length=200)
    street_address = models.CharField(max_length=200)
    municipality = models.CharField(max_length=100, blank=True)
    # county or county equivalent
    locality = models.CharField(max_length=100, blank=True)
    state = models.ForeignKey(State, blank=True, null=True, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=9, validators=[utils.validators.ZipCodeValidator])
    foia_email = models.EmailField("FOIA e-mail", null=True, blank=True)
    is_federal = models.BooleanField("Federal Agency?", default=False)
    is_public_body = models.BooleanField("Public Body?", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "entities"

class FoiaRequestBase(models.Model):
    """Represents the base content of a FOIA Request (i.e. everything but the entity/entities the request is going to)"""
    short_description = models.CharField(max_length=100)
    date_filed = models.DateTimeField(default=timezone.now)
    requested_formats = TaggableManager(verbose_name="Requested Format")
    requested_records = models.TextField()
    expedited_processing = models.TextField(
        verbose_name="justification for expedited processing",
        blank=True
    )
    fee_waiver = models.TextField(
        verbose_name="fee waiver justification",
        blank=True
    )
    related_project = models.ForeignKey("Project", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.short_description

    class Meta:
        verbose_name = "FOIA Request Body"
        verbose_name_plural = "FOIA Request Bodies"

@reversion.register(fields=["status", "fee_assessed", "modifications", "expedited_processing_granted"])
class FoiaRequestItem(models.Model):
    """A model representing a single FOIA request to a single agency"""
    request_content = models.ForeignKey(FoiaRequestBase, on_delete=models.CASCADE)
    agency = models.ForeignKey(Entity, on_delete=models.CASCADE)
    # this doesn't link to a source because in a lot of cases, we won't know the officer's name
    # and we can link our actual contacts to a FOIA request.
    recipient_name = models.CharField("name of public records officer", max_length=150)
    status = models.CharField(max_length=2, choices=FoiaStatus.choices, default=FoiaStatus.NO_RESPONSE)
    expedited_processing_granted = models.BooleanField(default=False, help_text="Did the agency grant your request for expedited processing?")
    fee_assessed = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    modifications = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        null=True,
        help_text="list any modifications you've made to your original request"
    )
    time_completed = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.request_content} ({self.agency})"

    class Meta:
        verbose_name = "FOIA Request"

@reversion.register
class Source(models.Model):

    class Gender(models.TextChoices):
        MAN = "m", _("Man")
        WOMAN = "w", _("Woman")
        NONCONFORMING = "n", _("Nonconforming")
        INAPPLICABLE = "i", _("Inapplicable")
        UNKNOWN = "u", _("Unknown")

    class Race(models.TextChoices):
        POC = "poc", _("Person of color")
        WHITE = "w", _("White")
        UNKNOWN = "unk", _("Unknown")

    class SourceType(models.TextChoices):
        """The category of a given source. Use `FOIA Officer` when applicable; otherwise,
        use whichever category fits best.
        """
        DATA_ADMIN = "db", _("Database administrator")
        REAL_PERSON = "rp", _("Person affected (anecdotal source)")
        EXPERT = "e", _("Expert")
        PR = "pr", _("Spokesperson, PR-Rep")
        FOIA = "f", _("Public Records officer")
        OFFICIAL = "o", _("Public/Company official")
        INSIDER = "i", _("Company or business employee (current or former)")

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200, blank=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, null=True, blank=True)
    work_number = PhoneNumberField(blank=True, null=True)
    home_number = PhoneNumberField(blank=True, null=True)
    cell_number = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=400, blank=True)
    twitter = models.CharField(max_length=16, blank=True,  validators=[utils.validators.TwitterHandleValidator])
    gender = models.CharField(max_length=1, choices=Gender.choices)
    race = models.CharField(max_length=3, choices=Race.choices)
    source_type = models.CharField(max_length=2, choices=SourceType.choices)
    notes = models.TextField(
        help_text="Random notes about this person.",
        blank=True
        )
    time_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        """Returns the source's full name."""
        if not (self.first_name or self.last_name):
            return None
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        if self.full_name is None:
            if self.entity is None:
                return ""
            return f"Unknown ({self.entity.name})" 
        return self.full_name

    class Meta:
        ordering = ["last_name", "first_name"]

@reversion.register(fields=["answered", "ground_rules"])
class Contact(models.Model):
    """Reflects an interview, interview attempt, email, phone call, etc."""

    CONTACT_METHOD_CHOICES = (
        ("e", "e-mail"),
        ("p", "Phone"),
        ("t", "Text"),
        ("i", "In-person"),
        ("l", "Letter")
    )
    
    GROUND_RULES_CHOICES = (
        ("otr", "On-the-record"),
        ("bg", "On background"),
        ("db", "Deep Background"),
        ("or", "Off-the-record")
    )

    time = models.DateTimeField(
        default=timezone.now,
        help_text="The time of the contact"
    )
    contact_method = models.CharField(
        max_length=1,
        choices=CONTACT_METHOD_CHOICES
        )
    answered = models.BooleanField(
        help_text="Has this person answered your attempt to reach them?"
    )
    short_description = models.CharField(
        max_length=500,
    )
    addl_notes = models.TextField(
        "additional notes", 
        blank=True
        )
    ground_rules = models.CharField(
        max_length=3,
        choices=GROUND_RULES_CHOICES,
        default="otr"
    )
    audio_file = models.FileField(upload_to="audio_files/", blank=True, null=True)
    transcript = models.FileField(upload_to="audio_transcript/", blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    related_project = models.ForeignKey("Project", blank=True, null=True, on_delete=models.CASCADE)

    def interview_type(self):
        interview_description = ""
        ground_rules = dict(self.GROUND_RULES_CHOICES)[self.ground_rules]
        interview_description += ground_rules
        contact_method = dict(self.CONTACT_METHOD_CHOICES)[self.contact_method]
        interview_description += " " + contact_method
        # phone or in-person
        if self.contact_method in { "p", "i" }:
            interview_description += " Interview"
            if not self.answered:
                interview_description += " Attempt"
        return interview_description

    def __str__(self):
        return f"{self.interview_type()} with {self.source} on {self.time}"

class Story(models.Model):

    class StoryType(models.TextChoices):
        INVESTIGATIVE = "i", _("investigative")
        EXPLANATORY = "x", _("explanatory")
        BREAKING = "b", _("breaking news")
        DATA = "d", _("data-driven piece")
        ENTERTAINMENT = "e", _("entertainment")

    headline = models.CharField(max_length=100)
    link = models.URLField(max_length=300)
    publication = models.ForeignKey("Publication", on_delete=models.CASCADE)
    sources = models.ManyToManyField(Source)
    interviews = models.ManyToManyField(Contact)
    project = models.ForeignKey("Project", on_delete=models.CASCADE, blank=True, null=True)
    story_type = models.CharField(max_length=1, choices=StoryType.choices)
    tags = TaggableManager()
    publication_date = models.DateField(default=get_current_date)

    def __str__(self):
        return self.headline

    class Meta:
        verbose_name_plural = "stories"

@reversion.register
class Project(models.Model):
    short_description = models.CharField(
        max_length=100,
        help_text="Enter a 6-word description of the piece"
        )
    long_description = models.TextField(
        help_text="Provide a more detailed description of the project"
        )
    tags = TaggableManager()
    completed = models.BooleanField(default=False)
    launch_time = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.short_description

class Document(models.Model):
    name = models.CharField(max_length=100)
    short_description = models.CharField(max_length=400)
    addl_notes = models.TextField(
        "additional notes",
        blank=True
        )
    doc_file = models.FileField("file", upload_to="documents/")
    foia_request = models.ForeignKey(FoiaRequestItem, verbose_name="FOIA Request", on_delete=models.CASCADE, blank=True, null=True)
    related_project = models.ForeignKey("Project", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Publication(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField(max_length=250)

    def __str__(self):
        return self.name

@reversion.register
class ProjectTask(models.Model):
    short_description = models.CharField(max_length=150)
    description = models.TextField(max_length=1000)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    task_started = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)