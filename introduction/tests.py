from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid domain", response.content.decode())
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_without_shell_for_valid_hostname(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup ok", b"")
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(response.status_code, 200)
        self.assertIn("lookup ok", response.content.decode())
