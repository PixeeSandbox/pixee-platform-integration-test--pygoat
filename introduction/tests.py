import subprocess
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_windows_branch_uses_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"windows stdout", b"")
        mock_popen.return_value = process

        for domain in ["example.com", "example.com; rm -rf /"]:
            with self.subTest(domain=domain):
                request = self.factory.post(
                    "/cmd_lab",
                    {"domain": f"https://www.{domain}", "os": "win"},
                )
                request.user = self.user

                response = cmd_lab(request)

                self.assertEqual(response.status_code, 200)
                command_args, command_kwargs = mock_popen.call_args
                self.assertEqual(command_args[0], ["nslookup", domain])
                self.assertNotIn("shell", command_kwargs)
                self.assertEqual(command_kwargs["stdout"], subprocess.PIPE)
                self.assertEqual(command_kwargs["stderr"], subprocess.PIPE)
                mock_popen.reset_mock()

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_unix_branch_uses_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"unix stdout", b"")
        mock_popen.return_value = process

        for domain in ["example.com", "example.com; rm -rf /"]:
            with self.subTest(domain=domain):
                request = self.factory.post(
                    "/cmd_lab",
                    {"domain": f"https://www.{domain}", "os": "linux"},
                )
                request.user = self.user

                response = cmd_lab(request)

                self.assertEqual(response.status_code, 200)
                command_args, command_kwargs = mock_popen.call_args
                self.assertEqual(command_args[0], ["dig", domain])
                self.assertNotIn("shell", command_kwargs)
                self.assertEqual(command_kwargs["stdout"], subprocess.PIPE)
                self.assertEqual(command_kwargs["stderr"], subprocess.PIPE)
                mock_popen.reset_mock()
