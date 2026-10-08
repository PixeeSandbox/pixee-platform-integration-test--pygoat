from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"dig output", b"")
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])

        request = self.factory.post("/", {"domain": "example.com", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(response.content.decode(), "dig output")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])

        request = self.factory.post("/", {"domain": "example.com;whoami", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content.decode(), "Something went wrong")
