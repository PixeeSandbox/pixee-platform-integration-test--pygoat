import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .views import _normalize_lookup_target


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    def test_normalize_lookup_target_rejects_option_like_prefixes(self):
        self.assertIsNone(_normalize_lookup_target("@8.8.8.8"))
        self.assertIsNone(_normalize_lookup_target("+trace"))
        self.assertIsNone(_normalize_lookup_target("-example.com"))

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_invalid_target_before_subprocess(self, run_mock):
        response = self.client.post("/cmd_lab", {"domain": "@8.8.8.8", "os": "linux"})

        run_mock.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]["output"], "Invalid lookup target")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_ipv6_lookup(self, run_mock):
        run_mock.return_value = subprocess.CompletedProcess(
            args=["dig", "2001:db8::1"],
            returncode=0,
            stdout="lookup ok\n",
            stderr="",
        )

        response = self.client.post("/cmd_lab", {"domain": "2001:db8::1", "os": "linux"})

        run_mock.assert_called_once_with(
            ["dig", "2001:db8::1"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]["output"], "lookup ok\n")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_accepts_punycode_hostname(self, run_mock):
        run_mock.return_value = subprocess.CompletedProcess(
            args=["nslookup", "xn--e1afmkfd.xn--p1ai"],
            returncode=0,
            stdout="punycode ok\n",
            stderr="",
        )

        response = self.client.post("/cmd_lab", {"domain": "пример.рф", "os": "win"})

        run_mock.assert_called_once_with(
            ["nslookup", "xn--e1afmkfd.xn--p1ai"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]["output"], "punycode ok\n")

    def test_normalize_lookup_target_accepts_https_url_with_www_prefix(self):
        self.assertEqual(_normalize_lookup_target("https://www.example.com"), "example.com")

    def test_normalize_lookup_target_ignores_url_path_and_query(self):
        self.assertEqual(
            _normalize_lookup_target("http://www.example.com/path?q=1#frag"),
            "example.com",
        )

    def test_normalize_lookup_target_rejects_invalid_url_port(self):
        self.assertIsNone(_normalize_lookup_target("https://example.com:bad"))

    def test_normalize_lookup_target_rejects_srv_style_underscores(self):
        self.assertIsNone(_normalize_lookup_target("_sip._tcp.example.com"))
