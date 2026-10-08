from django.test import TestCase

from .views import _is_valid_hostname


class HostnameValidationTests(TestCase):
    def test_accepts_normal_hostname(self):
        self.assertTrue(_is_valid_hostname('example.com'))

    def test_rejects_leading_hyphen_hostname(self):
        self.assertFalse(_is_valid_hostname('-example.com'))

    def test_rejects_consecutive_dots(self):
        self.assertFalse(_is_valid_hostname('example..com'))

    def test_rejects_shell_metacharacters(self):
        self.assertFalse(_is_valid_hostname('example.com;rm -rf /'))

    def test_rejects_overlong_label(self):
        self.assertFalse(_is_valid_hostname(f"{'a' * 64}.com"))
