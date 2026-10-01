from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.subprocess.Popen")
    @patch("introduction.views.subprocess.run")
    @patch("introduction.views.render")
    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self, mock_render, mock_run, mock_popen):
        mock_render.return_value = HttpResponse("Something went wrong")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]["output"], "Something went wrong")
