from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_running_command(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = SimpleNamespace(is_authenticated=True)
        mock_render.return_value = HttpResponse("Something went wrong")

        response = cmd_lab(request)

        self.assertFalse(mock_popen.called)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertContains(response, "Something went wrong")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = SimpleNamespace(is_authenticated=True)
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"resolved", b"")
        mock_render.return_value = HttpResponse("resolved")

        response = cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "resolved"},
        )
        self.assertContains(response, "resolved")
