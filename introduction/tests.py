import subprocess

from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock(is_authenticated=True)

    def _render_response(self, *args, **kwargs):
        return HttpResponse("rendered")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_valid_request_uses_argv_without_shell(self, mock_popen, mock_render):
        mock_render.side_effect = self._render_response
        process = Mock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], subprocess.PIPE)
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        mock_render.assert_called_once_with(
            request, "Lab/CMD/cmd_lab.html", {"output": "lookup output"}
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_invalid_domain_is_rejected_before_execution(self, mock_popen, mock_render):
        mock_render.side_effect = self._render_response

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request, "Lab/CMD/cmd_lab.html", {"output": "Invalid domain"}
        )
