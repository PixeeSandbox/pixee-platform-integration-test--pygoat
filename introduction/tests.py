from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _build_request(self, domain, os_value="linux"):
        request = self.factory.post("/cmd_lab3", {"domain": domain, "os": os_value})
        request.user = self.user
        return request

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_malicious_domain_without_invoking_subprocess(self, popen_mock):
        request = self._build_request("example.com; rm -rf /")

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain name")
        popen_mock.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_without_shell(self, popen_mock):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        popen_mock.return_value = process
        request = self._build_request("example.com")

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
