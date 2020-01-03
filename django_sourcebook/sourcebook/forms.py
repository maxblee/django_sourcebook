from django import forms
from sourcebook.models import FoiaRequestBase, FoiaRequestItem

class FoiaRequestBaseForm(forms.ModelForm):

    class Meta:
        model = FoiaRequestBase
        exclude = ("date_filed", )
        labels = {
            "short_description": "Subject Line",
        }
        help_texts = {
            "short_description": "Enter a subject line for this request. This is automatically prepended by the name of the public records act you are filing the request under (e.g. '2017 FOIA Logs' becomes 'FOIA Request: 2017 FOIA Logs')",
            "requested_records": "Precisely identify the records you are requesting, adding any additional information that might help the public records officer handle your request.",
            "related_project": "If this is related to a project you are currently working on, include the name of the project here."
        }

FoiaRequestFormSet = forms.modelformset_factory(
    FoiaRequestItem,
    fields=("agency", "recipient_name",),
    extra=1,
)