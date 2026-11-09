from django.test import TestCase

from .views import build_lookup_command


class CmdLabLookupTests(TestCase):
    def test_normal_hostname_is_accepted(self):
        command = build_lookup_command("example.com", "win")
        self.assertEqual(command, ["nslookup", "example.com"])

    def test_shell_metacharacters_or_whitespace_are_rejected(self):
        with self.assertRaises(ValueError):
            build_lookup_command("example.com; rm -rf /", "linux")
