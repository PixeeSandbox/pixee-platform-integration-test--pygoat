from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="cmdlabuser", password="password123")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; echo pwned", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", content)
        self.assertNotIn("pwned", content)
        mock_popen.assert_not_called()
