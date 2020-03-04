from django.contrib import admin
from reversion.admin import VersionAdmin
from sourcebook.models import (
    Source,
    Contact,
    Story,
    Publication,
    Project,
    ProjectTask,
    Document,
    FoiaRequestBase,
    FoiaRequestItem,
    FoiaStatus,
    ScheduledFoiaContent,
    ScheduledFoiaAgency,
    Entity,
    State,
)


@admin.register(ScheduledFoiaContent)
class ScheduledFoiaRequestContent(admin.ModelAdmin):
    pass


@admin.register(ScheduledFoiaAgency)
class ScheduledFoiaRequestForAgency(admin.ModelAdmin):
    pass


@admin.register(FoiaRequestBase)
class FoiaRequestBaseAdmin(admin.ModelAdmin):
    search_fields = ["short_description", "requested_records"]
    list_display = ("short_description", "date_filed")


@admin.register(FoiaRequestItem)
class FoiaRequestItemAdmin(VersionAdmin):
    search_fields = ["agency__name", "request_content__short_description"]
    list_display = (
        "request_content",
        "agency",
        "date_filed",
        "status",
        "time_completed",
    )

    def date_filed(self, obj):
        return obj.request_content.date_filed


# Register your models here.
@admin.register(Source)
class SourceAdmin(VersionAdmin):
    list_display = ("full_name", "title", "entity")


@admin.register(Contact)
class ContactAdmin(VersionAdmin):
    list_display = ("interview_type", "source", "time")

    def interview_type(self, obj):
        return obj.interview_type()


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("headline", "publication", "publication_date")


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(VersionAdmin):
    list_display = ("short_description", "launch_time", "completed")


@admin.register(ProjectTask)
class ProjectTaskAdmin(VersionAdmin):
    list_display = ("short_description", "task_started", "last_modified", "completed")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    search_fields = ["name", "short_description", "foia_request"]
    autocomplete_fields = ["foia_request"]


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ("name", "municipality", "locality")


@admin.register(State)
class StateAdmin(VersionAdmin):
    pass
