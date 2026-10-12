import subprocess

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch, MagicMock

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password123")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_and_uses_safe_subprocess(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("ok")

        malicious_request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "win"},
        )
        malicious_request.user = self.user

        response = cmd_lab3(malicious_request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        mock_render.assert_called_once_with(
            malicious_request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )

        mock_run.reset_mock()
        mock_render.reset_mock()
        mock_run.return_value = MagicMock(stdout="example.com.\n", stderr="")

        benign_request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )
        benign_request.user = self.user

        response = cmd_lab3(benign_request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        mock_render.assert_called_once_with(
            benign_request,
            "Lab/CMD/cmd_lab.html",
            {"output": "example.com.\n"},
        )
