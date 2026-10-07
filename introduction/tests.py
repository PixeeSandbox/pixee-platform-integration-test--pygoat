import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmd-user",
            password="safe-password",
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = MagicMock(stdout=b"lookup ok\n", stderr=b"")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertContains(response, "lookup ok")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self, mock_run):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
