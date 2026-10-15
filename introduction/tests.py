from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; id", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.content, b"rendered")
        self.assertEqual(mock_render.call_args[0][1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(mock_render.call_args[0][2]["output"], "Something went wrong")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domains(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        mock_run.return_value.stdout = "resolved"
        mock_run.return_value.stderr = ""

        for os_value, expected_command in (("win", "nslookup"), ("linux", "dig")):
            with self.subTest(os=os_value):
                request = self.factory.post(
                    "/cmd_lab3",
                    {"domain": "example.com", "os": os_value},
                )
                request.user = SimpleNamespace(is_authenticated=True)

                response = cmd_lab3(request)

                self.assertEqual(response.content, b"rendered")
                mock_run.assert_called_once()
                called_args, called_kwargs = mock_run.call_args
                self.assertEqual(called_args[0], [expected_command, "example.com"])
                self.assertFalse(called_kwargs.get("shell", False))
                self.assertTrue(called_kwargs["capture_output"])
                self.assertTrue(called_kwargs["text"])
                mock_run.reset_mock()
