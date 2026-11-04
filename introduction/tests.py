from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="testpassword123",
        )
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {
                    "domain": "example.com; whoami",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"safe output", b"")

            response = self.client.post(
                self.url,
                {
                    "domain": "example.com",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "safe output")
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])
