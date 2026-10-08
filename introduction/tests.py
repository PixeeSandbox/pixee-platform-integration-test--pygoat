from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process_mock = Mock()
        process_mock.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process_mock
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post("/cmd_lab3/", {"domain": "example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=mock_popen.call_args.kwargs["stdout"],
            stderr=mock_popen.call_args.kwargs["stderr"],
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("invalid")

        request = self.factory.post("/cmd_lab3/", {"domain": "example.com; rm -rf /", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
