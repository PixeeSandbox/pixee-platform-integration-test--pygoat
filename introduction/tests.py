from django.test import SimpleTestCase

from .views import _normalize_and_validate_domain


class CmdLabValidationTests(SimpleTestCase):
    def test_valid_domain_is_accepted(self):
        self.assertEqual(_normalize_and_validate_domain("https://www.example.com"), "example.com")

    def test_invalid_domain_is_rejected(self):
        self.assertIsNone(_normalize_and_validate_domain("example.com; rm -rf /"))
