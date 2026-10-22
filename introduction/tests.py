from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3RegressionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_expected_binary_for_valid_hostname(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        process_mock = Mock()
        process_mock.communicate.return_value = (b"stdout", b"")
        mock_popen.return_value = process_mock

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )

        mock_popen.reset_mock()
        process_mock.communicate.return_value = (b"stdout", b"")

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.org", "os": "linux"},
        )
        request.user = self.user

        other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.org"],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
