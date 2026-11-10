import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="test-pass123",
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"stdout", b"stderr")
        mock_popen.return_value = process
        mock_render.return_value = Mock()

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = Mock()

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com;whoami", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_not_called()
        self.assertEqual(mock_render.call_args.args[2], {"output": "Something went wrong"})
