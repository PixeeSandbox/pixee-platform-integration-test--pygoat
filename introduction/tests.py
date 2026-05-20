from django.test import TestCase

from .views import _normalize_lookup_target


class LookupTargetValidationTests(TestCase):
    def test_accepts_hostname_and_ip_literals(self):
        self.assertEqual(_normalize_lookup_target("example.com"), "example.com")
        self.assertEqual(_normalize_lookup_target("8.8.8.8"), "8.8.8.8")
        self.assertEqual(_normalize_lookup_target("localhost"), "localhost")

    def test_rejects_url_like_and_shell_injection_inputs(self):
        for value in [
            "https://example.com",
            "example.com:80",
            "example.com/path",
            "example.com;rm -rf /",
            "example .com",
            "exa_mple.com",
        ]:
            with self.subTest(value=value):
                self.assertIsNone(_normalize_lookup_target(value))
