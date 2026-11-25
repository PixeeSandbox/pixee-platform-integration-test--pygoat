from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_valid_hostname_uses_fixed_executable_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        self.client.post("/cmd_lab", {"domain": "www.example.com", "os": "win"})

        self.assertEqual(popen.call_args.args[0], ["nslookup", "www.example.com"])
        self.assertFalse(popen.call_args.kwargs["shell"])

    @patch("introduction.views.subprocess.Popen")
    def test_malicious_hostname_is_rejected(self, popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; id", "os": "win"})

        self.assertContains(response, "Invalid hostname")
        popen.assert_not_called()
