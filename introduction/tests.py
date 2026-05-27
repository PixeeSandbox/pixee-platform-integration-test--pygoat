from django.test import SimpleTestCase

from .views import _normalize_cmd_lab_domain


class CmdLabDomainNormalizationTests(SimpleTestCase):
    def test_accepts_https_url_with_www(self):
        self.assertEqual(_normalize_cmd_lab_domain("HTTPS://www.Example.com"), "example.com")

    def test_accepts_plain_domain_and_ip(self):
        self.assertEqual(_normalize_cmd_lab_domain("example.com"), "example.com")
        self.assertEqual(_normalize_cmd_lab_domain("192.168.0.1"), "192.168.0.1")

    def test_rejects_malicious_or_option_like_input(self):
        self.assertIsNone(_normalize_cmd_lab_domain("-example.com"))
        self.assertIsNone(_normalize_cmd_lab_domain("example.com; rm -rf /"))
        self.assertIsNone(_normalize_cmd_lab_domain("http://example.com/path"))
        self.assertIsNone(_normalize_cmd_lab_domain("http://example.com:80"))
