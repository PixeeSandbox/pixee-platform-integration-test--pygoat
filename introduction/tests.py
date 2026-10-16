from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch

import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword123",
        )
        self.client.force_login(user)

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab3",
                {
                    "domain": "example.com; rm -rf /",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argv_list_without_shell(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"lookup output", b"")

            response = self.client.post(
                "/cmd_lab3",
                {
                    "domain": "example.com",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertContains(response, "lookup output")
