from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_post_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs.get("shell", False))

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
