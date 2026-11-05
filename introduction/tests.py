from django.contrib.auth import get_user_model
from django.test import TestCase
import subprocess
from unittest.mock import MagicMock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="tester", password="pass12345")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_domain_uses_argument_list(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab", {"domain": "Example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "example output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid input")
        mock_popen.assert_not_called()
