from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_nslookup_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"resolved", b"")
        mock_popen.return_value = process

        request = self.factory.post("/cmd_lab", data={"domain": "example.com", "os": "win"})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_dig_argument_list_and_idna_normalization(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"resolved", b"")
        mock_popen.return_value = process

        domain = "münich.com"
        request = self.factory.post("/cmd_lab", data={"domain": domain, "os": "linux"})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", domain.encode("idna").decode("ascii")],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_accepts_url_input_and_normalizes_hostname(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"resolved", b"")
        mock_popen.return_value = process

        request = self.factory.post("/cmd_lab", data={"domain": "https://www.example.com", "os": "linux"})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "www.example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(mock_render.call_args[0][2], {"output": "Something went wrong"})
