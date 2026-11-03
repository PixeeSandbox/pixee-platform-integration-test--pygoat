from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="Password123!")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_arguments_on_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"windows ok", b"")
        mock_popen.return_value = process
        self.client.force_login(self.user)

        response = self.client.post("/cmd_lab", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], views.subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], views.subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_arguments_on_non_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"linux ok", b"")
        mock_popen.return_value = process
        self.client.force_login(self.user)

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], views.subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], views.subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post("/cmd_lab", {"domain": "example.com;whoami", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
