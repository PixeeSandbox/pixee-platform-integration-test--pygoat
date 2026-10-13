from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("Something went wrong")
        request = self.factory.post("/cmd_lab3", {"domain": "example.com; id", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertFalse(mock_popen.called)
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]["output"], "Something went wrong")
        self.assertEqual(response.content, b"Something went wrong")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")
        mock_render.return_value = HttpResponse("ok")
        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(response.content, b"ok")
