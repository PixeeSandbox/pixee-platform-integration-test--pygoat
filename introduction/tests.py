from django.test import TestCase, RequestFactory
from unittest.mock import patch

from django.contrib.auth import get_user_model
import subprocess

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "example.com;id", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["dig", "example.com;id"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup output")
