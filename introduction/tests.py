from unittest.mock import ANY, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="pass12345")
        self.client = Client()
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_invocation_for_windows(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"windows-ok", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(["nslookup", "example.com"], stdout=ANY, stderr=ANY)
        self.assertContains(response, "windows-ok")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_invocation_for_linux(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"linux-ok", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(["dig", "example.com"], stdout=ANY, stderr=ANY)
        self.assertContains(response, "linux-ok")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injection_style_domain(self, mock_popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
