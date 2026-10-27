from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

import introduction.other_views as other_views
import introduction.views as views

from introduction.other_views import cmd_lab3
from introduction.views import cmd_lab


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password123")

    def _post_request(self, path, data):
        request = self.factory.post(path, data)
        request.user = self.user
        return request

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_shell_metacharacters_without_popen(self, mock_popen):
        request = self._post_request(
            "/cmd_lab3",
            {"domain": "example.com; whoami", "os": "linux"},
        )

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup ok", b"")
        request = self._post_request(
            "/cmd_lab3",
            {"domain": "Example.COM", "os": "linux"},
        )

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("lookup ok", response.content.decode())
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters_without_popen(self, mock_popen):
        request = self._post_request(
            "/cmd_lab",
            {"domain": "example.com; whoami", "os": "win"},
        )

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup ok", b"")
        request = self._post_request(
            "/cmd_lab",
            {"domain": "Example.COM", "os": "win"},
        )

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("lookup ok", response.content.decode())
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
