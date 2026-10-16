from types import SimpleNamespace
from unittest.mock import patch

import subprocess

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _make_authenticated_post(self, domain, os_name="linux"):
        request = self.factory.post("/cmd_lab3", {"domain": domain, "os": os_name})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_safe_domain_uses_argv_list(self, mock_run, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])
        mock_run.return_value = subprocess.CompletedProcess(
            args=["dig", "example.com"],
            returncode=0,
            stdout="resolved",
            stderr="",
        )

        response = cmd_lab3(self._make_authenticated_post("example.com"))

        self.assertEqual(response.content, b"resolved")
        mock_run.assert_called_once_with(["dig", "example.com"], capture_output=True, text=True)
        self.assertNotIn("shell", mock_run.call_args.kwargs)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])

        response = cmd_lab3(self._make_authenticated_post("example.com; rm -rf /"))

        self.assertEqual(response.content, b"Something went wrong")
        mock_run.assert_not_called()
