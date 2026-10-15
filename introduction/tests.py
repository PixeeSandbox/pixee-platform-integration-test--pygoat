import subprocess
from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_hostname_uses_argument_list(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "example output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_hostname(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
