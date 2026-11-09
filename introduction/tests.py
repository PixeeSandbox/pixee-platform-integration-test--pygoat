import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"resolved", b"")
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context: HttpResponse(context.get("output", ""))

        request = self.factory.post("/cmd_lab/", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("resolved", response.content.decode())

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context.get("output", ""))

        request = self.factory.post("/cmd_lab/", {"domain": "example.com; rm -rf /", "os": "win"})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid domain", response.content.decode())
