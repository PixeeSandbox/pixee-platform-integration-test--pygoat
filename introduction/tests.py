from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmdtester",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)
        self.url = "/cmd_lab3"

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {
                    "domain": "example.com;whoami",
                    "os": "linux",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertFalse(mock_popen.called)

    def test_cmd_lab3_rejects_shell_metacharacters_before_lookup(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {
                    "domain": "example.com && cat /etc/passwd",
                    "os": "win",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertFalse(mock_popen.called)
