from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_without_shell_execution(self):
        user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.run") as mock_run, patch(
            "introduction.other_views.subprocess.Popen"
        ) as mock_popen:
            response = self.client.post(
                reverse("Command Injection Lab 3"),
                {
                    "domain": "example.com; whoami",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()
        mock_popen.assert_not_called()
