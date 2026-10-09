from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = type("User", (), {"is_authenticated": True})()

    def test_cmd_lab3_uses_argv_without_shell(self):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.run") as mock_run, patch(
            "introduction.other_views.render"
        ) as mock_render:
            mock_run.return_value = type(
                "Result",
                (),
                {"stdout": "resolved", "stderr": ""},
            )()
            mock_render.return_value = object()

            response = cmd_lab3(request)

        self.assertIs(response, mock_render.return_value)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["capture_output"], True)
        self.assertEqual(kwargs["text"], True)

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; id", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.run") as mock_run, patch(
            "introduction.other_views.render"
        ) as mock_render:
            mock_render.return_value = object()

            response = cmd_lab3(request)

        self.assertIs(response, mock_render.return_value)
        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(
            mock_render.call_args[0][2],
            {"output": "Something went wrong"},
        )
