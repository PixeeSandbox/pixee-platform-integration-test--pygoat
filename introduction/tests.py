from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_run):
        mock_run.return_value = Mock(stdout="resolved\n", stderr="")
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(["nslookup", "example.com"], capture_output=True, text=True)
        self.assertTrue(b"resolved" in response.content)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_injection_payload(self, mock_run):
        request = self.factory.post("/cmd_lab", {"domain": "example.com;id", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertTrue(b"Something went wrong" in response.content)
