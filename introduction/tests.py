import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLookupTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="lookup-user", password="test-password")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_invalid_domain_without_subprocess(self):
        invalid_domains = ["example.com; touch /tmp/injected", "invalid_domain", None]
        for domain in invalid_domains:
            with self.subTest(domain=domain), patch("introduction.other_views.subprocess.Popen") as popen:
                data = {"os": "linux"}
                if domain is not None:
                    data["domain"] = domain

                response = self.client.post("/cmd_lab3", data)

                self.assertEqual(response.status_code, 400)
                popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_safe_arguments_for_valid_domain(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b"lookup result", b"lookup warning")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup result")
        self.assertContains(response, "lookup warning")
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
