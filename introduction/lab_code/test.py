from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_hostname_uses_safe_argv(self, mock_popen, mock_render):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = mock_process
        mock_render.side_effect = lambda request, template, context=None: HttpResponse(
            context.get("output", "")
        )

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(response.content, b"lookup ok")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_hostname_uses_nslookup_on_windows(self, mock_popen, mock_render):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = mock_process
        mock_render.side_effect = lambda request, template, context=None: HttpResponse(
            context.get("output", "")
        )

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(response.content, b"lookup ok")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context=None: HttpResponse(
            context.get("output", "")
        )

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content, b"Something went wrong")
