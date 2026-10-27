from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"example output", b"")

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertIn("example output", response.content.decode())

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
