from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password123")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_shell_free_argument_list(self, mock_run, mock_render):
        mock_run.return_value = Mock(stdout="example output\n", stderr="")
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "linux"})
        request.user = self.user

        response = views.cmd_lab(request)

        mock_run.assert_called_once_with(["dig", "example.com"], capture_output=True, text=True)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "example output\n"},
        )
        self.assertEqual(response.content, b"rendered")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertEqual(response.content, b"rendered")
