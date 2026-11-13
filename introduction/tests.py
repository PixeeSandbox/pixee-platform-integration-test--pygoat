import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="password")
        self.factory = RequestFactory()

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_command_injection_domain(self, popen):
        request = self.factory.post("/cmd_lab3", {"domain": "example.com; id", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_is_passed_as_separate_shell_free_argument(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b"lookup output", b"")
        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
