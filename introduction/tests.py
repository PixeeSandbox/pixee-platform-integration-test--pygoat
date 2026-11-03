from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmd_tester",
            password="safe-password",
        )

    def _request(self, domain, os_value):
        request = self.factory.post("/cmd_lab/", {"domain": domain, "os": os_value})
        request.user = self.user
        return request

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_windows_branch_uses_argument_list(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b"windows output", b"")

        cmd_lab(self._request("example.com", "win"))

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_non_windows_branch_uses_argument_list(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b"unix output", b"")

        cmd_lab(self._request("example.com", "linux"))

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_malicious_domain_is_rejected_before_subprocess(self, mock_popen, mock_render):
        cmd_lab(self._request("example.com;whoami", "win"))

        mock_popen.assert_not_called()
