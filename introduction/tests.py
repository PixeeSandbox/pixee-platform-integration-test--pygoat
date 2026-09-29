from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_with_shell_disabled(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process
        mock_render.return_value = SimpleNamespace(status_code=200)

        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args[1]["shell"])
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "example output"},
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = SimpleNamespace(status_code=200)

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
