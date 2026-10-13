import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="cmd_lab_user", password="password123")

    def _build_request(self, domain, os_value):
        request = self.factory.post("/cmd_lab3", {"domain": domain, "os": os_value})
        request.user = self.user
        return request

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_list_for_windows(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")
        mock_render.return_value = HttpResponse("rendered")

        response = cmd_lab3(self._build_request("https://www.example.com", "win"))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_list_for_non_windows(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b"lookup output", b"")
        mock_render.return_value = HttpResponse("rendered")

        response = cmd_lab3(self._build_request("example.com", "linux"))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")

        response = cmd_lab3(self._build_request("example.com; rm -rf /", "win"))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(mock_render.call_args.args[2]["output"], "Something went wrong")
