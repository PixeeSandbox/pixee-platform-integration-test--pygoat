import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertIn(b"Something went wrong", response.content)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_and_shell_disabled(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"example output", b"")

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn(b"example output", response.content)
