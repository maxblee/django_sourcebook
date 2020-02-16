from django.core import validators
from django.core.validators import EmailValidator
from django import forms
from django import urls
from django.db.models import Q
from sourcebook.models import (
    Entity,
    FoiaRequestBase,
    FoiaRequestItem,
    Source
)



class MultiEmailField(forms.CharField):
    def clean(self, value):
        if value in validators.EMPTY_VALUES:
            return value
        text_content = super().clean(value)
        emails = [email_addr.strip() for email_addr in text_content.split(",")]
        for email_addr in emails:
            EmailValidator()(email_addr)
        return emails

class FoiaRequestBaseForm(forms.ModelForm):

    cc = MultiEmailField(help_text="Comma-separated list of email addresses to CC", required=False)
    bcc = MultiEmailField(help_text="Comma-separated list of email addresses to BCC", required=False)

    class Meta:
        model = FoiaRequestBase
        exclude = ("date_filed",)
        labels = {
            "short_description": "Subject Line",
        }
        help_texts = {
            "short_description": "Enter a subject line for this request. This is automatically prepended by the name of the public records act you are filing the request under (e.g. '2017 FOIA Logs' becomes 'FOIA Request: 2017 FOIA Logs')",
            "requested_records": "Precisely identify the records you are requesting, adding any additional information that might help the public records officer handle your request.",
            "related_project": "If this is related to a project you are currently working on, include the name of the project here.",
        }

    field_order = ["short_description", "cc", "bcc", "requested_records"]


FoiaRequestFormSet = forms.modelformset_factory(
    FoiaRequestItem, fields=("agency", "recipient",), extra=1,
)
# only show agencies that
FoiaRequestFormSet.form.base_fields["agency"].queryset = Entity.objects.filter(
    Q(foia_email__isnull=False)
)

FoiaRequestFormSet.form.base_fields["recipient"].queryset = Source.objects.none()