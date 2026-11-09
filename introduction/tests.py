from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com;id", "os": "win"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_render.call_args.args[1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(mock_render.call_args.args[2]["output"], "Something went wrong")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_safe_argument_list_for_benign_domain(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_render.call_args.args[2]["output"], "lookup ok")
