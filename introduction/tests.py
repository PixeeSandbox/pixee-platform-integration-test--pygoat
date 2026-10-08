from django.test import TestCase

from .views import _build_cmd_lab_command


class CmdLabCommandTests(TestCase):
    def test_builds_nslookup_command_for_windows(self):
        self.assertEqual(_build_cmd_lab_command("example.com", "win"), ["nslookup", "example.com"])

    def test_builds_dig_command_for_non_windows(self):
        self.assertEqual(_build_cmd_lab_command("example.com", "linux"), ["dig", "example.com"])

    def test_rejects_malicious_or_invalid_domains(self):
        for bad_domain in [
            "example.com;rm -rf /",
            "example.com && id",
            "-example.com",
            "example.com|whoami",
            "example.com\nwhoami",
        ]:
            with self.subTest(bad_domain=bad_domain):
                with self.assertRaises(ValueError):
                    _build_cmd_lab_command(bad_domain, "win")
