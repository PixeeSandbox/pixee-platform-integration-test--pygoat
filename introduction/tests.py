from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com;whoami", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = self.user
        mock_process = Mock()
        mock_process.communicate.return_value = (b"example output", b"")

        with patch(
            "introduction.other_views.subprocess.Popen",
            return_value=mock_process,
        ) as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertIn(b"example output", response.content)
