from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock(is_authenticated=True)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_hostname_uses_safe_argument_list(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post("/cmd_lab/", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], views.subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], views.subprocess.PIPE)
        mock_render.assert_called_once_with(request, "Lab/CMD/cmd_lab.html", {"output": "lookup output"})
        self.assertEqual(response.content, b"ok")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_invalid_domain_without_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("fallback")

        request = self.factory.post("/cmd_lab/", {"domain": "example.com; rm -rf /", "os": "linux"})
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, "Lab/CMD/cmd_lab.html", {"output": "Something went wrong"})
        self.assertEqual(response.content, b"fallback")
