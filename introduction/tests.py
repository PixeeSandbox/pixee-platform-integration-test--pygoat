import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab_uses_argument_list_for_benign_domain(self):
        process = MagicMock()
        process.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as popen:
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": "https://www.example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup ok")

    def test_cmd_lab_rejects_malicious_domain_before_popen(self):
        with patch("introduction.views.subprocess.Popen") as popen:
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": "example.com; rm -rf /", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
