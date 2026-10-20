from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_request(self, domain, os_value="win"):
        request = self.factory.post("/cmd_lab/", {"domain": domain, "os": os_value})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_payload(self, popen_mock):
        request = self._build_request("example.com; rm -rf /")

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
        popen_mock.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_list_command_for_valid_domain(self, popen_mock):
        process = popen_mock.return_value
        process.communicate.return_value = (b"resolved", b"")
        request = self._build_request("https://www.example.com")

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("resolved", response.content.decode())
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
