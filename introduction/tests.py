from django.test import SimpleTestCase

from .views import _is_safe_hostname


class CommandInjectionValidationTests(SimpleTestCase):
    def test_allows_valid_hostnames(self):
        for domain in ["example.com", "sub.example.co.uk", "localhost", "example.com."]:
            with self.subTest(domain=domain):
                self.assertTrue(_is_safe_hostname(domain))

    def test_rejects_invalid_hostnames(self):
        for domain in ["bad domain", "-evil.com", "a;rm -rf /", "example.com&&id", "", None]:
            with self.subTest(domain=domain):
                self.assertFalse(_is_safe_hostname(domain))
