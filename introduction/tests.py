from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def _render_response(self, request, template_name, context=None, *args, **kwargs):
        context = context or {}
        return HttpResponse(context.get("output", ""))

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, popen_mock, render_mock):
        render_mock.side_effect = self._render_response
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com;whoami", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        popen_mock.assert_not_called()
        self.assertContains(response, "Invalid domain input")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_without_shell(self, popen_mock, render_mock):
        render_mock.side_effect = self._render_response
        popen_mock.return_value.communicate.return_value = (b"example output", b"")
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell"))
        self.assertContains(response, "example output")
