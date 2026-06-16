from django.test import SimpleTestCase

from .views import _is_valid_domain, _normalize_domain


class CmdLabDomainValidationTests(SimpleTestCase):
    def test_normalize_domain_strips_scheme_and_www_consistently(self):
        self.assertEqual(_normalize_domain("https://www.example.com"), "example.com")
        self.assertEqual(_normalize_domain("www.example.com"), "example.com")

    def test_is_valid_domain_rejects_injection_payload(self):
        self.assertFalse(_is_valid_domain("example.com;id"))

    def test_is_valid_domain_accepts_hostname_and_ip(self):
        self.assertTrue(_is_valid_domain("example.com"))
        self.assertTrue(_is_valid_domain("127.0.0.1"))
