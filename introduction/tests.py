from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="StrongPassw0rd!",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_list_form_subprocess(self, mock_run, mock_render):
        mock_run.return_value = type("ProcessResult", (), {"stdout": "lookup ok", "stderr": ""})()
        mock_render.return_value = HttpResponse("rendered")

        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertNotIn("shell", mock_run.call_args.kwargs)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")

        request = self.factory.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        mock_run.assert_not_called()
        self.assertEqual(mock_render.call_args.args[2]["output"], "Something went wrong")
