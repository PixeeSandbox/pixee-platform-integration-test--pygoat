import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmd-test", password="password")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_invalid_domains_without_starting_process(self, popen):
        for domain in ("example.com;whoami", "-flag", "bad_domain"):
            with self.subTest(domain=domain):
                response = self.client.post("/cmd_lab", {"domain": domain, "os": "linux"})
                self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
