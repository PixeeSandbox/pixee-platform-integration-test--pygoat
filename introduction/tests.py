from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch
import subprocess

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_malicious_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"safe output", b"")

        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com; rm -rf /"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("safe output", response.content.decode())
