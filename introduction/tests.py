from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; cat /etc/passwd", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab3_invokes_subprocess_with_argument_list(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"resolved", b"")

            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args.args[0],
            ["nslookup", "example.com"],
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
