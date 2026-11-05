from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, Mock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="test-password",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_and_disables_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com; rm -rf /"],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertFalse(mock_popen.call_args.kwargs.get("shell", False))
