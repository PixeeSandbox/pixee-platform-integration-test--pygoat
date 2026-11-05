from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("invalid")
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com;id", "os": "linux"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(mock_popen.call_count, 0)
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(mock_render.call_args[0][2]["output"], "Invalid domain provided")
        self.assertEqual(response.content, b"invalid")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_without_shell_for_valid_hostname(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"stdout", b"stderr")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("valid")
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b"valid")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], other_views.subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], other_views.subprocess.PIPE)
