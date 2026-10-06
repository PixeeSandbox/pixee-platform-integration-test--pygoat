import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_post_uses_argument_list(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"result\n", b"")
        mock_popen.return_value = process

        request = self.factory.post("/cmd_lab", {"domain": "https://www.example.com", "os": "linux"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, "result")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
