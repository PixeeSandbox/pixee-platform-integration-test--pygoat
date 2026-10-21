import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="pass12345",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_benign_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"benign output", b"")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
        self.assertIs(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertIs(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)
        self.assertEqual(response.context["output"], "benign output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(response.context["output"], "Invalid domain")
