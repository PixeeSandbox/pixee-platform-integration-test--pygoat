import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="cmdlab-user", password="password123")

    def _build_request(self, domain, os_value="linux"):
        request = self.factory.post("/cmd_lab", data={"domain": domain, "os": os_value})
        request.user = self.user
        return request

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_argument_list_for_valid_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"example output", b"")

        response = cmd_lab(self._build_request("example.com", "linux"))

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "example output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injected_hostname_before_subprocess(self, mock_popen):
        response = cmd_lab(self._build_request("example.com; id", "linux"))

        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")
