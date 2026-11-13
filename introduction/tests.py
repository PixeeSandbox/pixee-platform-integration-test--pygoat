from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmdtest", password="password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_valid_hostname_runs_fixed_lookup_and_renders_output(self, popen):
        popen.return_value.communicate.return_value = (b"lookup result", b"lookup warning")

        response = self.client.post("/cmd_lab", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup resultlookup warning")
        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertIs(kwargs["shell"], False)

    @patch("introduction.views.subprocess.Popen")
    def test_invalid_hostname_is_rejected_without_running_lookup(self, popen):
        for domain in ("example.com; whoami", "-help", ""):
            with self.subTest(domain=domain):
                response = self.client.post("/cmd_lab", {"domain": domain, "os": "linux"})

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Something went wrong")
        popen.assert_not_called()
