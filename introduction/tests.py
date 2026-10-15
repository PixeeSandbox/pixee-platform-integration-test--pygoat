from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="cmduser",
            password="Password123!",
        )

    def _login(self):
        self.assertTrue(
            self.client.login(username="cmduser", password="Password123!")
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        self._login()
        mock_run.return_value = Mock(stdout=b"resolved\n", stderr=b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args.args[0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        self.assertIn("resolved", response.content.decode())

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        self._login()

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertIn("Something went wrong", response.content.decode())
