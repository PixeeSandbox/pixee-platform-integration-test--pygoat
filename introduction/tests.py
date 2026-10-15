import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="StrongPass123!"
        )

    def _request(self, domain, os_value):
        request = self.factory.post("/cmd_lab", {"domain": domain, "os": os_value})
        request.user = self.user
        return request

    @patch("introduction.views.subprocess.Popen")
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process

        response = cmd_lab(self._request("https://www.example.com", "linux"))

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertContains(response, "lookup output")

    @patch("introduction.views.subprocess.Popen")
    def test_invalid_payload_is_rejected_before_popen(self, mock_popen):
        response = cmd_lab(self._request("example.com && id", "linux"))

        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")
