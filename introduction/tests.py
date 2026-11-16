import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Test(TestCase):
    def test_domain_is_passed_as_a_single_process_argument(self):
        user = get_user_model().objects.create_user(username="testuser", password="password")
        self.client.force_login(user)
        domain = "example.com; echo injected"
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            mock_popen.return_value.communicate.return_value = (b"lookup output", b"")

            self.client.post(
                reverse("Command Injection Lab 3"),
                {"domain": domain, "os": "linux"},
            )

            mock_popen.assert_called_once_with(
                ["dig", domain],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
