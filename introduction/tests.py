from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        self.client.login(username="tester", password="password123")

        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "google.com && whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid domain")
        mock_popen.assert_not_called()
