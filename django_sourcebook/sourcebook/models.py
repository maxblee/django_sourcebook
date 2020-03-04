from django.db import models
from django.db.models import Q
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.functional import cached_property
import pytz
import us
import holidays
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
    NO_RESPONSE = "nr", _("No Response")
    ACKNOWLEDGED = "a", _("Acknowledged")
    CLOSED_FULFILLED = "cf", _("Closed - No Redactions")
    CLOSED_REDACTED = "cr", _("Closed - Some Redactions")
    CLOSED_EXCESS_FEE = "ce", _("Closed - Did Not Pay Fee")
    CLOSED_DENIAL = "cd", _("Closed - Denied Request")
    APPEALED = "ap", _("Appealed")
    SUED = "s", _("Sued")
    CLOSED_NO_RECORDS = "cn", _("Closed - No Records")


def get_current_date():
    return timezone.now().date()


@reversion.register(fields=["foia_template"])
class State(models.Model):
    fips_code = models.CharField(
        max_length=2, validators=[utils.validators.validate_fips]
    )
    public_records_act_name = models.CharField(
        "name of state public records act", max_length=200, blank=True, null=True
    )
    foia_template = models.FileField(
        upload_to="foia_templates/",
        verbose_name="Public Records act template",
        validators=[utils.validators.validate_template_extension],
        blank=True,
        null=True,
    )
    # most states have a maximum response time allowed for agencies to respond to public records requests
    # but some do not :(
    maximum_response_time = models.PositiveSmallIntegerField(
        help_text="What is the maximum response time allowed under this state's public records act?",
        blank=True,
        null=True,
    )
    # states differ in whether the response time refers to business days or total days
    business_days = models.BooleanField(
        blank=True,
        null=True,
        help_text="Is the response time the number of business days or actual days to respond to requests?",
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
    # Require a unique constraint because we have to look up from a select/datalist
    # and we want to know we're filing the right thing.
    name = models.CharField(max_length=200, unique=True)
    street_address = models.CharField(max_length=200)
    municipality = models.CharField(max_length=100, blank=True)
    # county or county equivalent
    locality = models.CharField(max_length=100, blank=True)
    state = models.ForeignKey(State, blank=True, null=True, on_delete=models.CASCADE)
    zip_code = models.CharField(
        max_length=9, validators=[utils.validators.ZipCodeValidator]
    )
    foia_email = models.EmailField("FOIA e-mail", null=True, blank=True)
    is_federal = models.BooleanField("Federal Agency?", default=False)
    is_public_body = models.BooleanField("Public Body?", default=False)

    search_vector = SearchVectorField(null=True, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "entities"


@reversion.register
class Source(models.Model):
    class Gender(models.TextChoices):
        MAN = "m", _("Man")
        WOMAN = "w", _("Woman")
        NONCONFORMING = "n", _("Nonconforming")
        INAPPLICABLE = "i", _("N/A")
        UNKNOWN = "u", _("Unknown")

    class Race(models.TextChoices):
        POC = "poc", _("Person of color")
        WHITE = "w", _("White")
        NOT_APPLICABLE = "na", _("N/A")
        UNKNOWN = "unk", _("Unknown")

    class SourceType(models.TextChoices):
        """The category of a given source. Use `FOIA Officer` when applicable; otherwise,
        use whichever category fits best.
        """

        DATA_ADMIN = "db", _("Database administrator")
        REAL_PERSON = "rp", _("Person affected (anecdotal source)")
        EXPERT = "e", _("Expert")
        PR = "pr", _("Spokesperson, PR-Rep")
        FOIA = "f", _("Public Records Officer")
        OFFICIAL = "o", _("Public/Company Official")
        INSIDER = "i", _("Company or business employee (current or former)")
        MASS_NUMBER = "mn", _("General Inbox (e.g. Media Relations number)")

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200, blank=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, null=True, blank=True)
    work_number = PhoneNumberField(blank=True, null=True)
    home_number = PhoneNumberField(blank=True, null=True)
    cell_number = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=400, blank=True)
    twitter = models.CharField(
        max_length=16, blank=True, validators=[utils.validators.TwitterHandleValidator]
    )
    gender = models.CharField(max_length=1, choices=Gender.choices)
    race = models.CharField(max_length=3, choices=Race.choices)
    source_type = models.CharField(max_length=2, choices=SourceType.choices)
    notes = models.TextField(help_text="Random notes about this person.", blank=True)
    time_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    search_vector = SearchVectorField(null=True, editable=False)

    @property
    def entity_name(self):
        if self.entity:
            return str(self.entity)
        return "-"

    @property
    def full_name(self):
        """Returns the source's full name."""
        # return the name of the department/number if this isn't a person
        if self.source_type == Source.SourceType.MASS_NUMBER:
            return f"{self.title} ({self.entity})"
        if not (self.first_name or self.last_name):
            return None
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        if self.full_name is None:
            return "Unknown"
        return self.full_name

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [GinIndex(fields=["search_vector"])]


class FoiaContent(models.Model):
    """An abstract base class representing the core content of a FOIA Request.

    Used by both `FoiaRequestBase` and `ScheduledFoiaContent`."""

    short_description = models.CharField(max_length=100)
    requested_formats = TaggableManager(verbose_name="Requested format")
    requested_records = models.TextField()
    expedited_processing = models.TextField(
        verbose_name="justification for expedited processing", blank=True
    )
    fee_waiver = models.TextField(verbose_name="fee waiver justification", blank=True)
    related_project = models.ForeignKey(
        "Project", blank=True, null=True, on_delete=models.CASCADE
    )
    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        abstract = True
        indexes = [GinIndex(fields=["search_vector"])]


class ScheduledFoiaContent(FoiaContent):
    date_started = models.DateField(auto_now_add=True)
    date_stopped = models.DateField(
        null=True,
        blank=True,
        help_text="When do you want to stop running this scheduler?",
    )
    request_frequency = models.DurationField(
        help_text="How frequently do you want to have this request filed?"
    )
    request_period = models.BooleanField(
        "Have request go out to all records filed since the last time you ran the request"
    )


class FoiaRequestBase(FoiaContent):
    """Represents the base content of a FOIA Request (i.e. everything but the entity/entities the request is going to)"""

    date_filed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.short_description

    class Meta:
        verbose_name = "FOIA Request Body"
        verbose_name_plural = "FOIA Request Bodies"
        ordering = ("-date_filed",)


class ScheduledFoiaAgency(models.Model):
    request_content = models.ForeignKey(ScheduledFoiaContent, on_delete=models.CASCADE)
    agency = models.ForeignKey(Entity, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        "Source",
        on_delete=models.SET_NULL,
        limit_choices_to={"source_type": Source.SourceType.FOIA},
        null=True,
        blank=True,
    )
    # recipient_name = models.CharField("name of public records officer", max_length=150)


@reversion.register(
    fields=["status", "fee_assessed", "modifications", "expedited_processing_granted"]
)
class FoiaRequestItem(models.Model):
    """A model representing a single FOIA request to a single agency"""

    request_content = models.ForeignKey(
        FoiaRequestBase, on_delete=models.CASCADE, related_name="foia_requests"
    )
    agency = models.ForeignKey(Entity, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        Source,
        on_delete=models.SET_NULL,
        limit_choices_to={"source_type": Source.SourceType.FOIA},
        null=True,
        blank=True,
    )
    # # this doesn't link to a source because in a lot of cases, we won't know the officer's name
    # # and we can link our actual contacts to a FOIA request.
    # recipient_name = models.CharField(
    #     "name of public records officer", max_length=150, blank=True
    # )
    status = models.CharField(
        max_length=2, choices=FoiaStatus.choices, default=FoiaStatus.NO_RESPONSE
    )
    expedited_processing_granted = models.BooleanField(
        default=False,
        help_text="Did the agency grant your request for expedited processing?",
    )
    fee_assessed = models.DecimalField(
        max_digits=9, decimal_places=2, blank=True, null=True
    )
    modifications = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        null=True,
        help_text="list any modifications you've made to your original request",
    )
    time_completed = models.DateField(blank=True, null=True)

    @staticmethod
    def calculate_days(start_date, num_days, state_holidays, business=False):
        """Calculates the number of days required for a response.

        Parameters
        ----------
        start_date: datetime.date
            The first date (i.e. the exact date the request was filed)
            **Note:** This function adds a day to the response because
            most agencies don't start time until the day *after* a request
            was received.
        num_days: int
            The number of days (e.g. for a response)
        state_holidays: holidays.countries.united_states.UnitedStates
            Represents a dictionary-type object referring to the state/federal
            holidays (to calculate business days)
        business: bool
            Whether or not to include business days in the response.
        """
        if not (
            isinstance(start_date, datetime.date)
            or isinstance(start_date, datetime.datetime)
        ):
            raise ValueError("The start date must be a date or datetime")
        skipped_first = False  # mark true once you've moved forward 1 day
        rel_days_count = 0
        current_date = start_date
        while rel_days_count < num_days:
            current_date += datetime.timedelta(days=1)
            if not skipped_first:
                skipped_first = True
                continue
            is_holiday = (
                current_date.weekday() in {5, 6} or current_date in state_holidays
            )
            if is_holiday and business:
                continue
            rel_days_count += 1
        # allow for datetime.date --> but timezones don't work there
        # need not because datetime is subclass of date
        if not isinstance(current_date, datetime.datetime):
            return current_date
        return current_date.astimezone(pytz.utc).date()

    @cached_property
    def due_date(self):
        """The date when the request needs to be processed by."""
        state_abbr = "" if self.agency.state is None else self.agency.state.info.abbr
        if self.agency.state is None:
            expected_tz = "America/New_York"
        else:
            expected_tz = self.agency.state.info.capital_tz
        request_filed = self.request_content.date_filed.astimezone(
            pytz.timezone(expected_tz)
        )
        if self.agency.is_federal:
            # TODO: Should probably add this into separate "state"
            business = True
            num_days = 20
        elif self.agency.state is None:
            num_days = None
            business = None
        else:
            num_days = self.agency.state.maximum_response_time
            business = self.agency.state.business_days
        state_holidays = holidays.US(state=state_abbr)
        if num_days is None or business is None:
            return None
        return self.calculate_days(request_filed, num_days, state_holidays, business)

    @property
    def response_time(self):
        """The number of days it took for you to get responsive records."""
        if self.time_completed is None:
            return None
        return (self.time_completed - self.request_content.date_filed.date()).days

    def __str__(self):
        return f"{self.request_content} ({self.agency})"

    class Meta:
        verbose_name = "FOIA Request"


@reversion.register(fields=["answered", "ground_rules"])
class Contact(models.Model):
    """Reflects an interview, interview attempt, email, phone call, etc."""

    CONTACT_METHOD_CHOICES = (
        ("e", "e-mail"),
        ("p", "Phone"),
        ("t", "Text"),
        ("i", "In-person"),
        ("l", "Letter"),
    )

    GROUND_RULES_CHOICES = (
        ("otr", "On-the-record"),
        ("bg", "On background"),
        ("db", "Deep Background"),
        ("or", "Off-the-record"),
    )

    time = models.DateTimeField(
        default=timezone.now, help_text="The time of the contact"
    )
    contact_method = models.CharField(max_length=1, choices=CONTACT_METHOD_CHOICES)
    answered = models.BooleanField(
        help_text="Has this person answered your attempt to reach them?"
    )
    short_description = models.CharField(max_length=500,)
    addl_notes = models.TextField("additional notes", blank=True)
    ground_rules = models.CharField(
        max_length=3, choices=GROUND_RULES_CHOICES, default="otr"
    )
    audio_file = models.FileField(upload_to="audio_files/", blank=True, null=True)
    transcript = models.FileField(upload_to="audio_transcript/", blank=True, null=True)
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="contacts"
    )
    related_project = models.ForeignKey(
        "Project", blank=True, null=True, on_delete=models.CASCADE
    )
    related_foia_request = models.ForeignKey(
        "FoiaRequestItem",
        verbose_name="Related FOIA Request",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="If this contact is related to a FOIA request (e.g. to nag a FOIA officer), note that contact here",
    )

    def interview_type(self):
        interview_description = ""
        ground_rules = dict(self.GROUND_RULES_CHOICES)[self.ground_rules]
        interview_description += ground_rules
        contact_method = dict(self.CONTACT_METHOD_CHOICES)[self.contact_method]
        interview_description += " " + contact_method
        # phone or in-person
        if self.contact_method in {"p", "i"}:
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
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, blank=True, null=True
    )
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
        max_length=100, help_text="Enter a 6-word description of the piece"
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
    addl_notes = models.TextField("additional notes", blank=True)
    doc_file = models.FileField("file", upload_to="documents/")
    foia_request = models.ForeignKey(
        FoiaRequestItem,
        verbose_name="FOIA Request",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    related_project = models.ForeignKey(
        "Project", blank=True, null=True, on_delete=models.CASCADE
    )

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
