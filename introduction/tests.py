from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_command_injection_hostname(self, popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid hostname")
        popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_runs_valid_hostname_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
