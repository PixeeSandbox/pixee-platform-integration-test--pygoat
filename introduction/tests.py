from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="tester", password="password123")

    @patch("introduction.other_views.render", return_value=HttpResponse("ok"))
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"result", b"")
        mock_popen.return_value = process

        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = self.user

        cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        mock_render.assert_called_once_with(request, "Lab/CMD/cmd_lab.html", {"output": "result"})

    @patch("introduction.other_views.render", return_value=HttpResponse("ok"))
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, "Lab/CMD/cmd_lab.html", {"output": "Invalid domain"})
        self.assertEqual(response.content, b"ok")
