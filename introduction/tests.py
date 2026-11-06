from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlab3-user",
            password="password123",
        )

    def _build_request(self, domain, os_value):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": domain, "os": os_value},
        )
        request.user = self.user
        return request

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_hostname_uses_argument_list_without_shell(self, popen_mock):
        process = MagicMock()
        process.communicate.return_value = (b"example.com lookup\n", b"")
        popen_mock.return_value = process

        response = cmd_lab3(self._build_request("example.com", "linux"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"example.com lookup", response.content)
        popen_mock.assert_called_once()
        self.assertEqual(
            popen_mock.call_args.args[0],
            ["dig", "example.com"],
        )
        self.assertNotIn("shell", popen_mock.call_args.kwargs)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters(self, popen_mock):
        response = cmd_lab3(self._build_request("example.com;id", "linux"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Something went wrong", response.content)
        popen_mock.assert_not_called()
