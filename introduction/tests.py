from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_cmd_lab3_rejects_malicious_domain_without_running_subprocess(self):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; id", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.other_views.render", return_value=HttpResponse("rendered")) as mock_render:
            with patch("introduction.other_views.subprocess.run") as mock_run:
                response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]["output"], "Invalid domain")

    def test_cmd_lab3_runs_safe_argument_list_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        completed = type("Completed", (), {"stdout": "nslookup ok", "stderr": ""})()

        with patch("introduction.other_views.render", return_value=HttpResponse("rendered")) as mock_render:
            with patch("introduction.other_views.subprocess.run", return_value=completed) as mock_run:
                response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]["output"], "nslookup ok")
