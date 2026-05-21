from django.test import TestCase

from .views import _is_safe_hostname


class SafeHostnameTests(TestCase):
    def test_accepts_plain_hostname(self):
        self.assertTrue(_is_safe_hostname("example.com"))
        self.assertTrue(_is_safe_hostname("sub.example.co.uk"))

    def test_rejects_whitespace_shell_metacharacters_and_options(self):
        for value in [
            " example.com",
            "example.com ",
            "example.com\t",
            "example.com\n",
            "example.com;rm -rf /",
            "example.com|whoami",
            "example.com&&id",
            "-n",
        ]:
            with self.subTest(value=value):
                self.assertFalse(_is_safe_hostname(value))
