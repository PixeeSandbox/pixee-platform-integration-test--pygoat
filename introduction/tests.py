import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen, mock_render):
        malicious_domain = "example.com; whoami"
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"ok", b"")
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post("/cmd_lab/", {"domain": malicious_domain, "os": "win"})
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["nslookup", malicious_domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_non_windows(self, mock_popen, mock_render):
        malicious_domain = "example.org && id"
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"ok", b"")
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post("/cmd_lab/", {"domain": malicious_domain, "os": "linux"})
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["dig", malicious_domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
