import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_list_invocation_for_win_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"nslookup output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            reverse("cmd_lab"),
            {"domain": "example.com; whoami", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com; whoami"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIsInstance(mock_popen.call_args.args[0], list)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_list_invocation_for_non_win_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"dig output", b"")
        mock_popen.return_value = process

        response = self.client.post(
            reverse("cmd_lab"),
            {"domain": "example.org && id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.org && id"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIsInstance(mock_popen.call_args.args[0], list)
