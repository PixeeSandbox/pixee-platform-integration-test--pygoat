from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_invalid_domain_rejected_without_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "https://www.example.com; whoami",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post(
            "/cmd_lab3",
            {
                "domain": "https://www.example.com",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", called_kwargs)
