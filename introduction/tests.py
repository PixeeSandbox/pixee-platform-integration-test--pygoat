from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password123")

    @patch("introduction.views.subprocess.run")
    def test_valid_domain_uses_safe_subprocess_arguments(self, mock_run):
        mock_run.return_value = Mock(stdout="lookup output", stderr="")
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertEqual(response.status_code, 200)

    @patch("introduction.views.subprocess.run")
    def test_shell_metacharacters_are_rejected_before_subprocess(self, mock_run):
        request = self.factory.post("/cmd_lab", {"domain": "example.com;whoami", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
