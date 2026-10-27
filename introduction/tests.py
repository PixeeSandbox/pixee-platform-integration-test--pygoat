from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="security-test-user",
            password="testpassword123",
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_benign_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters_before_popen(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
