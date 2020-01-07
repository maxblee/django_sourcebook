import sys
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

sys.path.append(settings.BASE_DIR)
from utils import auth


class Command(BaseCommand):
    help = "Sets up GMail credentials"

    def handle(self, *args, **options):
        service = auth.get_service()
        auth.add_labels(service)
