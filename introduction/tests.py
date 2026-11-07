from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    def _request(self, data):
        request = self.factory.post("/cmd_lab3/", data)
        request.user = self.user
        return request

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("bad")
        request = self._request({"domain": "example.com; rm -rf /", "os": "linux"})

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertEqual(response.content, b"bad")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argv_for_safe_domain(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("ok")
        mock_run.return_value.stdout = "lookup ok\n"
        mock_run.return_value.stderr = ""
        request = self._request({"domain": "example.com", "os": "win"})

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            capture_output=True,
            text=True,
            shell=False,
        )
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "lookup ok\n"},
        )
        self.assertEqual(response.content, b"ok")
