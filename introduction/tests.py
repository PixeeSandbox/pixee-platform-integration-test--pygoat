import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_rejects_invalid_or_missing_domain_without_running_process(self, popen):
        for data in (
            {"domain": "example.com; id", "os": "linux"},
            {"os": "linux"},
        ):
            with self.subTest(data=data):
                response = self.client.post(self.url, data)

                self.assertEqual(response.status_code, 400)
                popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_valid_domain_uses_safe_argument_list(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        for os_value, expected_command, domain in (
            ("linux", ["dig", "example.com"], "example.com"),
            ("win", ["nslookup", "example.org"], "https://www.example.org"),
        ):
            with self.subTest(os=os_value):
                response = self.client.post(self.url, {"domain": domain, "os": os_value})

                self.assertEqual(response.status_code, 200)
                popen.assert_called_with(
                    expected_command,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

        self.assertEqual(popen.call_count, 2)
