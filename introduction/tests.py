from django.test import SimpleTestCase

from .views import _is_safe_domain


class SafeDomainValidatorTests(SimpleTestCase):
    def test_accepts_valid_fqdn(self):
        self.assertTrue(_is_safe_domain("example.com"))
        self.assertTrue(_is_safe_domain("sub.example.co.uk"))

    def test_rejects_single_label_and_bad_structure(self):
        self.assertFalse(_is_safe_domain("localhost"))
        self.assertFalse(_is_safe_domain("example"))
        self.assertFalse(_is_safe_domain("example.com/path"))

    def test_rejects_whitespace_and_shell_metacharacters(self):
        self.assertFalse(_is_safe_domain("example.com whoami"))
        self.assertFalse(_is_safe_domain("example.com;whoami"))
        self.assertFalse(_is_safe_domain("example.com|whoami"))
