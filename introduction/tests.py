from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_malicious_domain_is_rejected_and_does_not_invoke_popen(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user
        mock_render.return_value = HttpResponse("ok")

        response = other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.content, b"ok")
        self.assertEqual(mock_render.call_args.args[2]["output"], "Something went wrong")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argv_list_without_shell(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b"nslookup output", b"")
        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user
        mock_render.return_value = HttpResponse("ok")

        response = other_views.cmd_lab3(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        mock_render.assert_called_once()
        self.assertEqual(response.content, b"ok")
        self.assertEqual(mock_render.call_args.args[2]["output"], "nslookup output")
