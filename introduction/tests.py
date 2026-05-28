from django.test import SimpleTestCase

from .views import DOMAIN_PATTERN, normalize_cmd_domain


class DomainValidationTests(SimpleTestCase):
    def test_accepts_common_hostname_formats(self):
        self.assertTrue(DOMAIN_PATTERN.fullmatch("example.com"))
        self.assertTrue(DOMAIN_PATTERN.fullmatch("sub.example.co.uk"))
        self.assertTrue(DOMAIN_PATTERN.fullmatch("localhost"))
        self.assertEqual(normalize_cmd_domain("https://example.com/path?x=1"), "example.com")
        self.assertEqual(normalize_cmd_domain("example.com/path"), "example.com")

    def test_rejects_invalid_hostnames(self):
        self.assertFalse(DOMAIN_PATTERN.fullmatch(""))
        self.assertFalse(DOMAIN_PATTERN.fullmatch("example.com;rm -rf /"))
        self.assertFalse(DOMAIN_PATTERN.fullmatch("exa mple.com"))
        with self.assertRaises(ValueError):
            normalize_cmd_domain("")
        with self.assertRaises(ValueError):
            normalize_cmd_domain("example.com;rm -rf /")
