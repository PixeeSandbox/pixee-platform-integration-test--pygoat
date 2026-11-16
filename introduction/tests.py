import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.Popen")
    def test_windows_domain_uses_nslookup_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b"lookup output", b"")

        response = self.client.post(self.url, {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup output")
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_default_domain_uses_dig_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b"dig output", b"")

        response = self.client.post(self.url, {"domain": "https://www.example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dig output")
        popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_invalid_domains_are_rejected_without_starting_process(self, popen):
        for domain in ("example.com; echo injected", "", "-invalid.example"):
            with self.subTest(domain=domain):
                response = self.client.post(self.url, {"domain": domain, "os": "win"})
                self.assertEqual(response.status_code, 400)

        popen.assert_not_called()
