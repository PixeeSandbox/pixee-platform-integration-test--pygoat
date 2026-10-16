from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_run, mock_render):
        mock_run.return_value.stdout = "stdout"
        mock_run.return_value.stderr = "stderr"
        mock_render.return_value = HttpResponse("rendered")

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=ANY,
            stderr=ANY,
            text=True,
        )
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "stdoutstderr"},
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com; id", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        mock_run.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Invalid domain"},
        )
