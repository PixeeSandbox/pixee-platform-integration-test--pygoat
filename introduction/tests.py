from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": "example.com; rm -rf /", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        process = MagicMock()
        process.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": "https://www.example.com", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
