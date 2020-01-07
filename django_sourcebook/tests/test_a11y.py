import urllib.parse
from axe_selenium_python import Axe
from tests import SeleniumTestClass


class AccessibilityTestCase(SeleniumTestClass):
    def get_urls(self):
        url_extensions = {
            "",
            "sourcebook",
            "sourcebook/sources",
            "foia",
            "foia/foia-request",
            "foia/foia-request-list",
        }
        return {
            urllib.parse.urljoin(self.BASE_URL, extension)
            for extension in url_extensions
        }

    def test_accessibility(self):
        urls_to_test = self.get_urls()
        for url in urls_to_test:
            self.driver.get(url)
            axe = Axe(self.driver)
            axe.inject()
            results = axe.run()
            import time

            assert len(results["violations"]) == 0, (
                axe.report(results["violations"]),
                url,
            )
