from django.test import SimpleTestCase

from .views import _is_valid_hostname


class HostnameValidationTests(SimpleTestCase):
    def test_accepts_valid_hostnames(self):
        self.assertTrue(_is_valid_hostname("example.com"))
        self.assertTrue(_is_valid_hostname("localhost"))
        self.assertTrue(_is_valid_hostname("xn--p1ai.example"))

    def test_rejects_shell_injection_and_whitespace(self):
        self.assertFalse(_is_valid_hostname("example.com; rm -rf /"))
        self.assertFalse(_is_valid_hostname("example.com && whoami"))
        self.assertFalse(_is_valid_hostname("  "))
        self.assertFalse(_is_valid_hostname("bad host"))
