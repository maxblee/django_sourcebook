"""The module for sending FOIA requests."""
from collections import abc
import base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import os.path
import re
import sys

sys.path.append("..")
from django_sourcebook.settings import (
    MEDIA_ROOT,
    FEDERAL_FOIA_TEMPLATE,
    BASE_FOIA_TEMPLATE,
    FROM_EMAIL,
)
from django.template import Context, Template
from utils import auth
import mammoth

GMAIL_SERVICE = auth.get_service()
TEMPLATE_INFO = re.compile(r"{{\s*([a-zA-Z_]+)\s*}}")


class FoiaHandler(abc.Mapping):
    """A class designed to help file FOIA requests, given objects describing the content of the requests.

    Parameters
    ----------
    `request_body`: `FoiaRequestBase`
        The content of the overarching request (so everything but information about the agency and FOIA officer)
    `recipient_info`: `FoiaRequestItem`
        Information about the recipient (an `Entity` object and the name of the FOIA officer)
    """

    def __init__(self, request_body, recipient_info):
        # assume we're filing based on a specific request
        self.sending_base_request = False
        recipient_agency = recipient_info.agency
        self.template_path = self._get_template_path(recipient_agency)
        public_records_act = self._get_pra_name(recipient_agency)
        max_response_time = self._get_max_response_time(recipient_agency)
        self.request_information = {
            "subject_line": request_body.short_description,
            "requested_records": request_body.requested_records,
            "expedited_processing": request_body.expedited_processing,
            "fee_waiver": request_body.fee_waiver,
            "foia_email": recipient_agency.foia_email,
            "recipient_name": recipient_info.recipient_name
            if recipient_info.recipient_name != ""
            else "Public Records Officer",
            "public_records_act": public_records_act,
            "max_response_time": max_response_time,
            "agency_name": recipient_agency.name,
            "agency_street_address": recipient_agency.street_address,
            "agency_municipality": recipient_agency.municipality,
            "state": str(recipient_agency.state),
            "zip_code": recipient_agency.zip_code,
        }

    def __getitem__(self, item):
        return self.request_information[item]

    def __iter__(self):
        return iter(self.request_information)

    def __len__(self):
        return len(self.request_information)

    def _get_max_response_time(self, agency):
        max_resp_time = agency.state.maximum_response_time
        if max_resp_time is None:
            return max_resp_time
        interval = "business days" if agency.state.business_days else "days"
        return str(max_resp_time) + " " + interval

    def _get_pra_name(self, agency):
        """Returns the name of the public records act (for the subject line) given the Entity object (for the agency)"""
        if agency.is_federal:
            return "Freedom of Information Act"
        # If we don't have the name of the statute, just revert to stating we're filing a Public Records Act Request
        elif not agency.state.public_records_act_name:
            return "Public Records"
        return agency.state.public_records_act_name

    def _get_template_path(self, agency):
        """Get the path to a template given the Entity object for the agency."""
        template_directory = os.path.join(MEDIA_ROOT, "foia_templates")
        fallback = os.path.join(template_directory, BASE_FOIA_TEMPLATE)
        if agency.is_federal:
            expected_path = os.path.join(template_directory, FEDERAL_FOIA_TEMPLATE)
            if not os.path.exists(expected_path):
                if not os.path.exists(fallback):
                    raise OSError(
                        "Could not find federal FOIA. Check BASE_FOIA_TEMPLATE and FEDERAL_FOIA_TEMPLATE in settings."
                    )
                self.sending_base_request = True
                return fallback
            return expected_path
        else:
            expected_path = os.path.join(MEDIA_ROOT, str(agency.state.foia_template))
            if expected_path != "":
                if not os.path.exists(expected_path):
                    raise OSError(
                        "Could not find FOIA template at {}".format(str(expected_path))
                    )
                return expected_path
            else:
                if not os.path.exists(fallback):
                    raise OSError(
                        "Could not find the base template. Hint: Try checking the value of BASE_FOIA_TEMPLATE in settings"
                    )
                self.sending_base_request = True
                return fallback

    def _parse_field(self, key):
        if key == "recipient_name" and self["recipient_name"] == "":
            return "Public Records Officer"
        return self[key]

    def compose_request(self):
        html_template = Template(mammoth.convert_to_html(self.template_path).value)
        context = Context(self.request_information)
        text_template = Template(mammoth.extract_raw_text(self.template_path).value)
        return html_template.render(context), text_template.render(context)

    def file_request(self):
        send_labels = [
            label_id
            for _label, label_id in auth.get_label_ids(GMAIL_SERVICE).items()
            if _label in ["FOIA", "FOIA - UNFINISHED"]
        ]
        # https://stackoverflow.com/questions/35873847/mime-multipart-being-sent-as-noname-on-python-3
        message = MIMEMultipart("alternative")
        message["to"] = self["foia_email"]
        message["from"] = FROM_EMAIL
        message[
            "subject"
        ] = f"{self['public_records_act']} Request: {self._parse_field('subject_line')}"
        html_content, text_content = self.compose_request()
        mime_text = MIMEText(text_content, "text")
        mime_html = MIMEText(html_content, "html")
        message.attach(mime_text)
        message.attach(mime_html)
        # This part of the solution from https://stackoverflow.com/questions/42601324/python-3-6-gmail-api-send-email-with-attachement
        final_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
        sent_message = (
            GMAIL_SERVICE.users()
            .messages()
            .send(userId="me", body=final_message)
            .execute()
        )
        sent_message = (
            GMAIL_SERVICE.users()
            .messages()
            .modify(
                userId="me", id=sent_message["id"], body={"addLabelIds": send_labels}
            )
            .execute()
        )
        return sent_message
