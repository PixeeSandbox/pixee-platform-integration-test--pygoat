import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )

    def test_cmd_lab_rejects_malicious_domain_before_popen(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argv_and_disables_shell_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        process = type("Process", (), {})()
        process.communicate = lambda: (b"lookup ok", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertEqual(mock_popen.call_args.kwargs.get("shell", False), False)
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)
