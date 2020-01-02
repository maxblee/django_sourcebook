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
    FoiaRequest,
    Entity,
    State
)
# Register your models here.
@admin.register(Source)
class SourceAdmin(VersionAdmin):
    list_display = ("full_name", "title", "entity")

@admin.register(Contact)
class ContactAdmin(VersionAdmin):
    list_display = ("interview_type","source", "time")

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
    pass
@admin.register(FoiaRequest)
class FoiaRequestAdmin(VersionAdmin):
    list_display = ("short_description", "agency", "date_filed", "status", "time_completed")
@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("name", "municipality", "state")
@admin.register(State)
class StateAdmin(VersionAdmin):
    pass