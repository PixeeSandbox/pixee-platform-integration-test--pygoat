from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from types import SimpleNamespace
from unittest.mock import patch

import introduction.other_views as other_views
from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])
        mock_popen.return_value = SimpleNamespace(communicate=lambda: (b"valid output", b""))

        request = self.factory.post("/cmd_lab", {"domain": "https://www.example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"valid output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], other_views.subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], other_views.subprocess.PIPE)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])

        request = self.factory.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"Invalid domain")
        mock_popen.assert_not_called()
