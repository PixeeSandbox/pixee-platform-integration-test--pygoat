from django.test import SimpleTestCase

from .views import _is_valid_domain, _normalize_domain_input


class CmdLabDomainValidationTests(SimpleTestCase):
    def test_accepts_valid_hostname_and_trailing_dot(self):
        self.assertTrue(_is_valid_domain("example.com"))
        self.assertTrue(_is_valid_domain("sub.example.com."))
        self.assertTrue(_is_valid_domain("localhost"))

    def test_accepts_valid_ip_address(self):
        self.assertTrue(_is_valid_domain("192.0.2.10"))
        self.assertTrue(_is_valid_domain("2001:db8::1"))

    def test_normalizes_common_url_inputs_to_hostnames(self):
        self.assertEqual(_normalize_domain_input("https://www.example.com/path"), "example.com")
        self.assertEqual(_normalize_domain_input("http://example.com:8080/query"), "example.com")

    def test_rejects_missing_and_shell_metacharacters(self):
        self.assertFalse(_is_valid_domain(""))
        self.assertFalse(_is_valid_domain("example.com;rm -rf /"))
        self.assertFalse(_is_valid_domain("example.com|whoami"))
