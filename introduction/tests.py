from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("blocked")
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertFalse(mock_popen.called)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertEqual(response.content, b"blocked")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "valid-host.example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "valid-host.example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertIn("stdout", kwargs)
        self.assertIn("stderr", kwargs)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "example output"},
        )
        self.assertEqual(response.content, b"ok")
