from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="testpass123",
        )

    def test_cmd_lab_valid_hostname_uses_safe_subprocess_invocation(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.run", return_value=SimpleNamespace(stdout="example ok", stderr="")) as mock_run:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"example ok", response.content)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
        )

    def test_cmd_lab_rejects_malicious_domain_without_running_command(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.run") as mock_run:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid domain", response.content)
        mock_run.assert_not_called()
