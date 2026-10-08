from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username="cmdlabuser", password="testpass123")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.run") as mock_run:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; id", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lab/CMD/cmd_lab.html")
        self.assertContains(response, "Invalid domain name")
        mock_run.assert_not_called()
