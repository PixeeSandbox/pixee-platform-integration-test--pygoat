from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("blocked")
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"blocked")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_list_form_command_for_valid_domain(self, mock_run, mock_render):
        mock_run.return_value = SimpleNamespace(stdout="answer\n", stderr="")
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs.get("capture_output"), True)
        self.assertEqual(kwargs.get("text"), True)
        self.assertEqual(kwargs.get("check"), False)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "answer\n"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"rendered")
