import socket
from django.test.utils import override_settings
from django.core.management.commands.runserver import Command
from django.conf import settings
from django import test
from selenium import webdriver


class SeleniumTestClass(test.TestCase):
    # override_settings needed to pass accessibility tests and ensure functional behavior matches end user behavior
    def setUp(self):
        host = (
            "localhost" if settings.ALLOWED_HOSTS == [] else settings.ALLOWED_HOSTS[0]
        )
        port = Command.default_port
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = conn.connect_ex((host, int(port)))
        if result != 0:
            raise ConnectionError(
                "Could not connect to host and port. Try running `python manage.py runserver`"
            )
        self.BASE_URL = f"http://{host}:{port}"
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.close()
