from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

import introduction.views as views


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )
        self.url = reverse("Command Injection Lab")

    def test_cmd_lab_uses_argv_list_for_safe_domain(self):
        self.client.force_login(self.user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"stdout", b"stderr")

            response = self.client.post(
                self.url,
                {"domain": "example.com", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.context["output"], "stdoutstderr")

    def test_cmd_lab_rejects_injected_payload_without_subprocess_call(self):
        self.client.force_login(self.user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {"domain": "example.com;id", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(response.context["output"], "Something went wrong")
