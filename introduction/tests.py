from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def test_rejects_malicious_domain_without_shell_execution(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        client = Client()
        client.force_login(user)

        with patch("introduction.other_views.subprocess.Popen") as popen_mock:
            response = client.post(
                "/cmd_lab3",
                {
                    "domain": "example.com; id",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        popen_mock.assert_not_called()
