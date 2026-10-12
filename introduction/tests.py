from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (
            b"example.com.\tIN\tA\t93.184.216.34\n",
            b"",
        )
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertContains(response, "example.com.\tIN\tA\t93.184.216.34")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertFalse(mock_popen.called)
        self.assertContains(response, "Invalid domain")
