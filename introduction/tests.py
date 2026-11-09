from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
            password="password123",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_list_invocation_for_safe_hostname(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"dns output", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"ok")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=-1,
            stderr=-1,
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_hostname(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("invalid")

        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"invalid")
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
