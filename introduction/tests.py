from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import other_views, views


class CommandInjectionHardeningTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _authenticated_post(self, path, data):
        request = self.factory.post(path, data=data)
        request.user = Mock(is_authenticated=True)
        return request

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        request = self._authenticated_post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com;rm -rf /", "os": "win"},
        )

        mock_render.return_value = Mock(status_code=200)

        other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_invokes_popen_with_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process
        mock_render.return_value = Mock(status_code=200)
        request = self._authenticated_post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com", "os": "win"},
        )

        other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "lookup ok"},
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        request = self._authenticated_post(
            "/cmd_lab/",
            {"domain": "https://www.example.com&&whoami", "os": "linux"},
        )

        mock_render.return_value = Mock(status_code=200)

        views.cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_invokes_popen_with_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process
        mock_render.return_value = Mock(status_code=200)
        request = self._authenticated_post(
            "/cmd_lab/",
            {"domain": "https://www.example.com", "os": "linux"},
        )

        views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "lookup ok"},
        )
