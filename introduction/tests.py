from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_structured_subprocess_arguments(self, mock_run):
        mock_run.return_value = Mock(stdout="example output\n", stderr="")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertContains(response, "example output")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_run):
        response = self.client.post("/cmd_lab", {"domain": "example.com; whoami", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
