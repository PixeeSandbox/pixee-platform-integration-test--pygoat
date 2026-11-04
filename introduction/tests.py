from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            self.url,
            {
                "domain": "https://www.example.com;whoami",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_popen.assert_not_called()
