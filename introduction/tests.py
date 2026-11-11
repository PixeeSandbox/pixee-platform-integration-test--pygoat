import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-lab-user", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com;whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, popen):
        popen.return_value.communicate.return_value = (b"lookup result", b"")

        response = self.client.post("/cmd_lab", {"domain": "www.example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup result")
        popen.assert_called_once_with(
            ["dig", "www.example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
