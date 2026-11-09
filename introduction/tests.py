import subprocess
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="password123",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_without_shell(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        process = Mock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")

        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
