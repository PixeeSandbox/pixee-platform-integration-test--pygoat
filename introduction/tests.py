from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmd-test", password="password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_runs_without_a_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])

    @patch("introduction.other_views.subprocess.Popen")
    def test_requires_authentication(self, mock_popen):
        self.client.logout()

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login")
        mock_popen.assert_not_called()
