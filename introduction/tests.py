from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_shell_injection_domain(self, popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_runs_lookup_with_validated_hostname(self, popen):
        popen.return_value.communicate.return_value = (b"lookup result", b"")

        response = self.client.post("/cmd_lab", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertIs(kwargs["shell"], False)
