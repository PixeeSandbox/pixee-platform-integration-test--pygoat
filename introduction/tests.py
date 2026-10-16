from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        self.client.force_login(self.user)

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; whoami", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        self.client.force_login(self.user)

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"lookup output", b"")

            response = self.client.post(
                "/cmd_lab3",
                {"domain": "https://www.example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertFalse(kwargs.get("shell", False))
