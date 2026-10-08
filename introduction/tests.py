from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="cmdlab3-user", password="password123")

    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.run") as run_mock, patch(
            "introduction.other_views.render",
            return_value=HttpResponse("ok"),
        ) as render_mock:
            run_mock.return_value.stdout = "lookup output"
            run_mock.return_value.stderr = ""

            response = cmd_lab3(request)

        self.assertEqual(response.content, b"ok")
        run_mock.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotIn("shell", run_mock.call_args.kwargs)
        render_mock.assert_called_once()

    def test_cmd_lab3_rejects_shell_metacharacters_before_subprocess(self):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.run") as run_mock, patch(
            "introduction.other_views.render",
            side_effect=lambda req, template, context: HttpResponse(context["output"]),
        ) as render_mock:
            response = cmd_lab3(request)

        self.assertEqual(response.content, b"Something went wrong")
        run_mock.assert_not_called()
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2], {"output": "Something went wrong"})
