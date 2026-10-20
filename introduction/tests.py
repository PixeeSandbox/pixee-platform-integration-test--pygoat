from django.test import TestCase, RequestFactory
from types import SimpleNamespace
from unittest.mock import patch
import subprocess

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_vector_for_benign_domain(self, mock_popen, mock_render):
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)
        mock_process = SimpleNamespace(communicate=lambda: (b"ok", b""))
        mock_popen.return_value = mock_process
        mock_render.return_value = SimpleNamespace(status_code=200)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injected_domain_before_subprocess(self, mock_popen, mock_render):
        request = self.factory.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})
        request.user = SimpleNamespace(is_authenticated=True)
        mock_render.return_value = SimpleNamespace(status_code=200)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {"output": "Something went wrong"})
