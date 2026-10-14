from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmd_user",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout=b"resolved\n", stderr=b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(mock_run.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        self.assertContains(response, "resolved")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Invalid domain")
