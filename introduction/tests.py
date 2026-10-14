from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
        )

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com; id", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid input", response.content.decode())
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"lookup ok", b"")
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("lookup ok", response.content.decode())
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
