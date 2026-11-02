from django.test import TestCase

from introduction.views import _build_cmd_lab_command, _validate_cmd_lab_domain


class CmdLabValidationTests(TestCase):
    def test_valid_hostname_maps_to_expected_argv_for_windows_branch(self):
        self.assertEqual(
            _build_cmd_lab_command("example.com", "win"),
            ["nslookup", "example.com"],
        )

    def test_injected_value_is_rejected_before_execution(self):
        with self.assertRaises(ValueError):
            _build_cmd_lab_command("example.com;id", "win")

    def test_valid_hostname_passes_domain_validation(self):
        self.assertEqual(_validate_cmd_lab_domain("sub.example.com"), "sub.example.com")
