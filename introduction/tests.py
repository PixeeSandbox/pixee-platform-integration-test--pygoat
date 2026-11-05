from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_without_shell_for_valid_hostname(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"example", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b"ok")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])

    @patch("introduction.views.render", return_value=HttpResponse("blocked"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "evil.com;id", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b"blocked")
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
