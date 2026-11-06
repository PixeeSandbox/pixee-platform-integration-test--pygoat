from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def _render_response(self, request, template_name, context=None, *args, **kwargs):
        return HttpResponse((context or {}).get("output", ""))

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_popen(self, mock_popen, mock_render):
        mock_render.side_effect = self._render_response
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content.decode(), "Invalid domain")
        mock_popen.assert_not_called()
        mock_render.assert_called_once()

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen, mock_render):
        mock_render.side_effect = self._render_response
        process = mock_popen.return_value
        process.communicate.return_value = (b"example.com output", b"")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content.decode(), "example.com output")
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertIsInstance(called_args[0], list)
        self.assertEqual(called_args[0], ["nslookup", "example.com"])
        self.assertFalse(called_kwargs.get("shell", False))
