from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_and_skips_subprocess(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid domain", response.content)
        mock_popen.assert_not_called()
