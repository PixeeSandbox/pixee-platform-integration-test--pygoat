from django.test import SimpleTestCase

from .views import _validate_cmd_lab_domain


class CmdLabDomainValidationTests(SimpleTestCase):
    def test_accepts_normalized_domain(self):
        self.assertEqual(
            _validate_cmd_lab_domain("  https://www.example.com.  "),
            "example.com"
        )

    def test_rejects_shell_metacharacters(self):
        for payload in (
            "example.com; rm -rf /",
            "example.com && whoami",
            "example.com | cat /etc/passwd",
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    _validate_cmd_lab_domain(payload)
