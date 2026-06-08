from django.test import SimpleTestCase

from .views import _is_valid_lookup_domain, _normalize_lookup_domain


class CmdLabDomainValidationTests(SimpleTestCase):
    def test_normalize_extracts_hostname_from_url_and_port(self):
        self.assertEqual(
            _normalize_lookup_domain('https://www.example.com:8443/path?q=1'),
            'example.com',
        )

    def test_valid_domains_include_hosts_localhost_and_ips(self):
        self.assertTrue(_is_valid_lookup_domain(_normalize_lookup_domain('example.com')))
        self.assertTrue(_is_valid_lookup_domain(_normalize_lookup_domain('localhost')))
        self.assertTrue(_is_valid_lookup_domain(_normalize_lookup_domain('intranet')))
        self.assertTrue(_is_valid_lookup_domain(_normalize_lookup_domain('127.0.0.1')))
        self.assertTrue(_is_valid_lookup_domain(_normalize_lookup_domain('example.com:53')))

    def test_invalid_domains_reject_shell_metacharacters_and_whitespace(self):
        self.assertFalse(_is_valid_lookup_domain(_normalize_lookup_domain('example.com;id')))
        self.assertFalse(_is_valid_lookup_domain(_normalize_lookup_domain('example.com whoami')))
        self.assertFalse(_is_valid_lookup_domain(_normalize_lookup_domain('example.com\nwhoami')))
        self.assertFalse(_is_valid_lookup_domain(_normalize_lookup_domain('example.com/path')))
