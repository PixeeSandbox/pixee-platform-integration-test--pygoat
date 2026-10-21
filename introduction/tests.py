import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_safe_subprocess_arguments(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("ok")
        mock_run.return_value = SimpleNamespace(stdout=b"example output\n", stderr=b"")

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("blocked")

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
