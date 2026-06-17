from django.test import TestCase

from .views import _validate_cmd_domain


class CmdLabValidationTests(TestCase):
    def test_validate_cmd_domain_accepts_safe_inputs(self):
        self.assertEqual(_validate_cmd_domain("example.com"), "example.com")
        self.assertEqual(_validate_cmd_domain("LOCALHOST"), "localhost")
        self.assertEqual(_validate_cmd_domain("192.0.2.1"), "192.0.2.1")
        self.assertEqual(
            _validate_cmd_domain("https://www.example.com/path"),
            "example.com",
        )
        self.assertEqual(
            _validate_cmd_domain("münich.example"),
            "xn--mnich-kva.example",
        )

    def test_validate_cmd_domain_rejects_injection_and_invalid_inputs(self):
        self.assertIsNone(_validate_cmd_domain("example.com; cat /etc/passwd"))
        self.assertIsNone(_validate_cmd_domain("example.com && whoami"))
        self.assertIsNone(_validate_cmd_domain("example.com\nwhoami"))
        self.assertIsNone(_validate_cmd_domain("bad host"))
        self.assertIsNone(_validate_cmd_domain(" example.com"))
        self.assertIsNone(_validate_cmd_domain("example.com "))
        self.assertIsNone(_validate_cmd_domain("foo_bar.example.com"))
        self.assertIsNone(_validate_cmd_domain("a" * 64 + ".com"))
