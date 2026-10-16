from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="tester", password="password123")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = MagicMock(stdout="lookup ok\n", stderr="warning\n")
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)
        content = response.content.decode()

        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True, check=False)
        self.assertIn("lookup ok", content)
        self.assertIn("warning", content)
        self.assertLess(content.index("lookup ok"), content.index("warning"))

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_without_running_command(self, mock_run):
        request = self.factory.post("/cmd_lab", {"domain": "example.com; id", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
