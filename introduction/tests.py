from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3SecurityTest(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        user = get_user_model().objects.create_user(
            username="securitytester",
            password="strong-password-123",
        )
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                reverse("Command Injection Lab 3"),
                {
                    "domain": "example.com; rm -rf /",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain supplied")
        mock_popen.assert_not_called()
