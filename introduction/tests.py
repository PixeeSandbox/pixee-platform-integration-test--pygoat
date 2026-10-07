from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlab3-user",
            password="password123",
        )
        self.url = "/cmd_lab3"

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {
                "domain": "example.com; id",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        self.client.force_login(self.user)
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(
            self.url,
            {
                "domain": "example.com",
                "os": "win",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        command, kwargs = mock_popen.call_args
        self.assertEqual(command[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
