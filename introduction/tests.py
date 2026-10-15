from subprocess import CompletedProcess
from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_injected_domain_without_running_command(self, mock_run):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com;whoami", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = CompletedProcess(
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

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
            text=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
