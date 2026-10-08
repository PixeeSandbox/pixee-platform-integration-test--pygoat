from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_invocation(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"ok")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "lookup output"},
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("bad request")

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; whoami", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"bad request")
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
