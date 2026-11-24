import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="testuser", password="password")
        self.client.force_login(user)

    @patch("introduction.views.subprocess.Popen")
    def test_domain_is_passed_as_a_separate_argument_without_a_shell(self, mock_popen):
        domain = "example.com; echo injected"
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"lookup warning")

        response = self.client.post("/cmd_lab", {"domain": domain, "os": "win"})

        mock_popen.assert_called_once_with(
            ["nslookup", domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup outputlookup warning")
