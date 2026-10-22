from django.test import TestCase, RequestFactory
from unittest.mock import Mock, patch
from django.http import HttpResponse

from .other_views import cmd_lab3


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = type("User", (), {"is_authenticated": True})()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_run, mock_render):
        mock_run.return_value = Mock(stdout="lookup ok", stderr="")
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])

        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertEqual(response.content.decode(), "lookup ok")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_blocks_malicious_domain(self, mock_run, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])

        request = self.factory.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(response.content.decode(), "Something went wrong")
