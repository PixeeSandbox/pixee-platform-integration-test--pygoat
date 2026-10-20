import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="cmduser", password="password123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_and_returns_output(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"mock dns output", b"")

        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("mock dns output", response.content.decode())
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
        mock_popen.assert_not_called()
