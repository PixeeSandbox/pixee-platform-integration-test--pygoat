import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="cmduser", password="password")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_without_running_subprocess(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b"rendered")
        mock_run.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        mock_run.return_value = subprocess.CompletedProcess(
            args=["dig", "example.com"],
            returncode=0,
            stdout="lookup ok",
            stderr="",
        )
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b"rendered")
        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            capture_output=True,
            text=True,
        )
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "lookup ok"},
        )
