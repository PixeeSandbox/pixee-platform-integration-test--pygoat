from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import ANY, patch


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        self.assertTrue(self.client.login(username="testuser", password="testpass123"))
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_invalid_domain_before_popen(self, mock_popen):
        self.assertTrue(self.client.login(username="testuser", password="testpass123"))

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com && whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
