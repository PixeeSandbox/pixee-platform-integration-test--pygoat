import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"resolver output", b"")
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context=None, *args, **kwargs: HttpResponse(
            context.get("output", "")
        )

        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b"resolver output")
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        mock_render.assert_called_once_with(
            request, "Lab/CMD/cmd_lab.html", {"output": "resolver output"}
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injected_domain_before_command_execution(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context=None, *args, **kwargs: HttpResponse(
            context.get("output", "")
        )

        request = self.factory.post("/cmd_lab", {"domain": "example.com; id", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b"Invalid domain provided")
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request, "Lab/CMD/cmd_lab.html", {"output": "Invalid domain provided"}
        )
