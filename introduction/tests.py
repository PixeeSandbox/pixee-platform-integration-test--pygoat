import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import _normalize_cmd_domain, cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="testpass")

    def test_normalize_cmd_domain_allows_valid_hostnames(self):
        self.assertEqual(_normalize_cmd_domain("https://www.example.com"), "example.com")
        self.assertEqual(_normalize_cmd_domain("http://example.com"), "example.com")
        self.assertEqual(_normalize_cmd_domain("www.example.com"), "example.com")
        self.assertEqual(_normalize_cmd_domain("example.com/path"), "example.com")
        self.assertEqual(_normalize_cmd_domain("https://example.com/path"), "example.com")
        self.assertEqual(_normalize_cmd_domain("example.com:53"), "example.com")
        self.assertEqual(_normalize_cmd_domain("example.com"), "example.com")
        self.assertEqual(_normalize_cmd_domain("localhost"), "localhost")
        self.assertEqual(_normalize_cmd_domain("127.0.0.1"), "127.0.0.1")

    def test_normalize_cmd_domain_rejects_invalid_hostnames(self):
        self.assertIsNone(_normalize_cmd_domain("example.com;rm -rf /"))
        self.assertIsNone(_normalize_cmd_domain("example.com && whoami"))
        self.assertIsNone(_normalize_cmd_domain("example.com:abc"))
        self.assertIsNone(_normalize_cmd_domain("ftp://example.com"))
        self.assertIsNone(_normalize_cmd_domain("http://example.com?foo=bar"))
        self.assertIsNone(_normalize_cmd_domain("http://user@example.com"))
        self.assertIsNone(_normalize_cmd_domain(" example.com "))
        self.assertIsNone(_normalize_cmd_domain(""))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_and_strips_www_prefix(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_invalid_domain_without_executing_command(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com;rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_allows_ip_literals_as_single_arguments(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "127.0.0.1", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "127.0.0.1"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
