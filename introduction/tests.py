from django.test import TestCase

from introduction.views import _build_lookup_command, _sanitize_domain_for_lookup


class CommandLookupValidationTests(TestCase):
    def test_build_lookup_command_valid_hostname_for_both_os_branches(self):
        self.assertEqual(
            _build_lookup_command("https://www.example.com", "win"),
            ["nslookup", "example.com"],
        )
        self.assertEqual(
            _build_lookup_command("https://www.example.com", "linux"),
            ["dig", "example.com"],
        )

    def test_sanitize_domain_rejects_invalid_hostname_characters(self):
        for value in ("example.com; rm -rf /", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _sanitize_domain_for_lookup(value)
