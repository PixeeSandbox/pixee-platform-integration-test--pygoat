from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="StrongPass123")
        self.assertTrue(self.client.login(username="cmduser", password="StrongPass123"))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_linux_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"stdout data", b"stderr data")

        domain = "https://www.example.com;id"
        response = self.client.post("/cmd_lab", {"domain": domain, "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com;id"])
        self.assertNotIn("shell", kwargs)
        self.assertIn(b"stdout data", response.content)
        self.assertIn(b"stderr data", response.content)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_windows_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"win stdout", b"win stderr")

        domain = "https://www.example.org&&whoami"
        response = self.client.post("/cmd_lab", {"domain": domain, "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.org&&whoami"])
        self.assertNotIn("shell", kwargs)
        self.assertIn(b"win stdout", response.content)
        self.assertIn(b"win stderr", response.content)
