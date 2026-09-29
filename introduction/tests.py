from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_windows_lookup(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b"example result", b"")
        popen_mock.return_value = process
        render_mock.return_value = Mock()

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        popen_mock.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        render_mock.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "example result"},
        )
        self.assertIs(response, render_mock.return_value)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injection_like_domain(self, popen_mock, render_mock):
        render_mock.return_value = Mock()

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.com;whoami", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertIs(response, render_mock.return_value)
