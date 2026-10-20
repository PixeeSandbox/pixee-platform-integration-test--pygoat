from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlab3user",
            password="password123",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_and_shell_false(self, popen_mock, render_mock):
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"valid response", b"")
        popen_mock.return_value = process_mock
        render_mock.return_value = HttpResponse("ok")

        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        cmd_lab3(request)

        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(render_mock.call_args[0][1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(render_mock.call_args[0][2]["output"], "valid response")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, popen_mock, render_mock):
        render_mock.return_value = HttpResponse("ok")

        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "https://www.example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        cmd_lab3(request)

        popen_mock.assert_not_called()
        self.assertEqual(render_mock.call_args[0][1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(render_mock.call_args[0][2]["output"], "Something went wrong")
