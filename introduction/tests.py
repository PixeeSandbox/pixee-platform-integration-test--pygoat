from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
            password="password123",
        )

    @patch("introduction.other_views.render", return_value=HttpResponse("ok"))
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run, mock_render):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        mock_render.assert_called_once()

    @patch("introduction.other_views.render", return_value=HttpResponse("bad"))
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_injected_domain_before_subprocess(self, mock_run, mock_render):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; id", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
