from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="StrongPass123!",
        )

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        self.client.force_login(self.user)
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; id", "os": "linux"},
            )
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_list_arguments_for_valid_domain(self, mock_popen):
        self.client.force_login(self.user)
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
