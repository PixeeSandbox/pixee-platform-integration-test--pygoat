from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_run):
        mock_run.return_value = Mock(stdout="example output", stderr="")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_run.call_args.args[0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        self.assertContains(response, "example output")

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_run.assert_not_called()
