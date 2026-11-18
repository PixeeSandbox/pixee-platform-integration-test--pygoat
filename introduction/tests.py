import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_malicious_domain(self, mocked_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mocked_popen.assert_not_called()

    def test_valid_domain_uses_non_shell_argument_list(self):
        for os_option, executable in (("win", "nslookup"), ("linux", "dig")):
            with self.subTest(os=os_option), patch(
                "introduction.other_views.subprocess.Popen"
            ) as mocked_popen:
                mocked_popen.return_value.communicate.return_value = (b"lookup output", b"lookup error")

                response = self.client.post(
                    "/cmd_lab3",
                    {"domain": "www.example.com", "os": os_option},
                )

                mocked_popen.assert_called_once_with(
                    [executable, "www.example.com"],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertContains(response, "lookup output")
                self.assertContains(response, "lookup error")
