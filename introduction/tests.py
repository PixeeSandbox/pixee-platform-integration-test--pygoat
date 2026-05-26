from django.test import TestCase

from .views import _is_safe_hostname, _normalize_domain


class CmdLabValidationTests(TestCase):
    def test_normalize_domain_strips_url_prefix_and_path(self):
        self.assertEqual(
            _normalize_domain('https://www.example.com/path?x=1'),
            'example.com',
        )

    def test_safe_hostname_accepts_valid_domain(self):
        self.assertTrue(_is_safe_hostname('sub.example.co.uk'))

    def test_safe_hostname_rejects_malicious_input(self):
        self.assertFalse(_is_safe_hostname('example.com;rm -rf /'))
