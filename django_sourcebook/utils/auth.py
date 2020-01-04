"""
`auth.py` handles authentication for the Gmail API. It does not handle authentication for
Amazon AWS S3, which should be handled using Amazon's `awscli`.

The source code for this is derived from Better Government's FoiaMail project,
which is available from GitHub at 
[https://github.com/bettergov/foiamail](https://github.com/bettergov/foiamail)
and licensed under MIT. Specifically, the source code this section is derived from
is available [here](https://github.com/bettergov/foiamail/blob/master/auth/auth.py).
"""
import os.path
import json
import apiclient
import oauth2client.file
import oauth2client.tools
from oauth2client.client import OAuth2WebServerFlow
import sys
sys.path.append("..")
from django_sourcebook.settings import CREDENTIALS

CREDENTIAL_JSON = os.path.join(CREDENTIALS, "credentials.json")
CREDENTIAL_DAT = os.path.join(CREDENTIALS, "credentials.dat")

SCOPES = {
    "https://www.googleapis.com/auth/gmail.modify", 
    "https://www.googleapis.com/auth/gmail.labels"
}

def get_credentials():
    """Returns Google API Credentials, storing data in credentials directory"""
    storage = oauth2client.file.Storage(CREDENTIAL_DAT)
    client_json = json.load(open(CREDENTIAL_JSON))["installed"]
    client_id, client_secret = client_json["client_id"], client_json["client_secret"]
    credentials = storage.get()
    if credentials is None or credentials.invalid or \
        not credentials.has_scopes(SCOPES):
        flow = OAuth2WebServerFlow(client_id, client_secret, SCOPES)
        credentials = oauth2client.tools.run_flow(
            flow,
            storage,
            oauth2client.tools.argparser.parse_args(["--noauth_local_webserver"])
        )
    return credentials

def get_service(credentials=get_credentials()):
    """Gets GMail service, given credentials"""
    return apiclient.discovery.build("gmail", "v1", credentials=credentials)

def add_labels(service):
    """Adds labels for handling FOIA requests given the service (e.g. from `get_service`)"""
    foia_labels = ["FOIA", "FOIA - DONE", "FOIA - NA", "FOIA - UNFINISHED"]
    all_labels = service.users().labels().list(userId="me").execute()["labels"]
    user_added_labels = frozenset(
        { label["name"] for label in all_labels if label["type"] == "user" }
    )
    print("Creating Labels...")
    for label in foia_labels:
        if not label in user_added_labels:
            new_label = {
                "labelListVisibility":"labelShow",
                "messageListVisibility":"show",
                "name":label
            }
            service.users().labels().create(userId="me", body=new_label).execute()
            print(label)

def get_label_ids(service):
    """Returns labelIds given the service you're using. Used to add labels to messages"""
    all_labels = service.users().labels().list(userId="me").execute()
    return { label["name"]: label["id"] for label in all_labels["labels"] }