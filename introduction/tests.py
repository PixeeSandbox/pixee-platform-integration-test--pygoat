import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_domain_uses_argv(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"example.com\n", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "example.com")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injection_payload(self, mock_popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")
