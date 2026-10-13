from django.test import TestCase

from .other_views import _build_cmd_lab3_argv


class CmdLab3CommandTests(TestCase):
    def test_build_cmd_lab3_argv_windows_branch(self):
        self.assertEqual(
            _build_cmd_lab3_argv('https://www.example.com', 'win'),
            ['nslookup', 'example.com']
        )

    def test_build_cmd_lab3_argv_non_windows_branch(self):
        self.assertEqual(
            _build_cmd_lab3_argv('https://www.example.com', 'linux'),
            ['dig', 'example.com']
        )

    def test_malicious_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            _build_cmd_lab3_argv('example.com; rm -rf /', 'linux')
