from django.test import TestCase

from introduction.views import _build_dns_command


class CmdLabCommandTests(TestCase):
    def test_build_dns_command_normalizes_https_www_prefix_for_windows(self):
        self.assertEqual(
            _build_dns_command("https://www.example.com", "win"),
            ["nslookup", "example.com"],
        )

    def test_build_dns_command_normalizes_https_www_prefix_for_non_windows(self):
        self.assertEqual(
            _build_dns_command("https://www.example.com", "linux"),
            ["dig", "example.com"],
        )

    def test_build_dns_command_rejects_malicious_payloads(self):
        for payload in ("google.com; id", "google.com && dir"):
            with self.assertRaises(ValueError):
                _build_dns_command(payload, "win")
            with self.assertRaises(ValueError):
                _build_dns_command(payload, "linux")
