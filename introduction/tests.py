from django.test import RequestFactory, TestCase
from unittest.mock import ANY, Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock(is_authenticated=True)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com;rm -rf /", "os": "linux"}
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"}
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "example output")
