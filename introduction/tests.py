import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import _is_valid_cmd_domain, cmd_lab


class CmdDomainValidationTests(TestCase):
    def test_accepts_plain_hostname_and_url_forms(self):
        self.assertTrue(_is_valid_cmd_domain("example.com"))
        self.assertTrue(_is_valid_cmd_domain("sub.example.co.uk"))
        self.assertTrue(_is_valid_cmd_domain("https://www.example.com"))
        self.assertTrue(_is_valid_cmd_domain("HTTP://Example.com"))
        self.assertTrue(_is_valid_cmd_domain("xn--bcher-kva.example"))

    def test_rejects_non_hostname_forms_and_injection_payloads(self):
        self.assertFalse(_is_valid_cmd_domain(""))
        self.assertFalse(_is_valid_cmd_domain("  "))
        self.assertFalse(_is_valid_cmd_domain("localhost"))
        self.assertFalse(_is_valid_cmd_domain("192.0.2.10"))
        self.assertFalse(_is_valid_cmd_domain("2001:db8::1"))
        self.assertFalse(_is_valid_cmd_domain("https://example.com/path"))
        self.assertFalse(_is_valid_cmd_domain("example.com:53"))
        self.assertFalse(_is_valid_cmd_domain("foo:bar"))
        self.assertFalse(_is_valid_cmd_domain("user@example.com"))
        self.assertFalse(_is_valid_cmd_domain("example.com?query=1"))
        self.assertFalse(_is_valid_cmd_domain("[2001:db8::1]"))
        self.assertFalse(_is_valid_cmd_domain("example.com && whoami"))


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_invalid_domain_returns_error_before_subprocess(self, popen_mock, render_mock):
        render_mock.return_value = HttpResponse("ok")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com && whoami", "os": "linux"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertEqual(response.status_code, 200)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_invocation(self, popen_mock, render_mock):
        process = MagicMock()
        process.communicate.return_value = ("answer", "")
        popen_mock.return_value = process
        render_mock.return_value = HttpResponse("ok")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab(request)

        popen_mock.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
