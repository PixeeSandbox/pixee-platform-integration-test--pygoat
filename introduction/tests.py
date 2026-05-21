from django.test import SimpleTestCase

from introduction.views import _normalize_domain_input


class NormalizeDomainInputTests(SimpleTestCase):
    def test_accepts_plain_domain(self):
        self.assertEqual(_normalize_domain_input('example.com'), 'example.com')

    def test_strips_legacy_https_www_prefix(self):
        self.assertEqual(_normalize_domain_input('https://www.example.com'), 'example.com')

    def test_allows_trailing_dot(self):
        self.assertEqual(_normalize_domain_input('example.com.'), 'example.com.')

    def test_rejects_idna_domain(self):
        self.assertIsNone(_normalize_domain_input('пример.рф'))

    def test_rejects_shell_metacharacters(self):
        self.assertIsNone(_normalize_domain_input('example.com; rm -rf /'))
