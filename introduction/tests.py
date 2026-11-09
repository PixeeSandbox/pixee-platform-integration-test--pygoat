from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import subprocess

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_and_disables_shell(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "lookup output"},
        )
        self.assertEqual(response.content, b"ok")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("invalid")

        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertEqual(response.content, b"invalid")
