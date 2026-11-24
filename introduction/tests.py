import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_domain_is_passed_as_a_separate_command_argument(self):
        user = get_user_model().objects.create_user(username="cmd-test", password="password")
        self.client.force_login(user)
        domain = "example.com; echo injected"

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_popen.return_value.communicate.return_value = (b"lookup result\n", b"lookup warning\n")
            response = self.client.post("/cmd_lab", {"domain": domain, "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "lookup result")
        self.assertContains(response, "lookup warning")
