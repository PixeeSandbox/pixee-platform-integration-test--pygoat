import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="pass12345",
        )
        self.url = "/cmd_lab"

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell_for_safe_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = process
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "safe output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
