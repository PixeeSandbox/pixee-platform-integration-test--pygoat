from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from introduction.other_views import cmd_lab3
from unittest.mock import Mock, patch
import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="tester", password="password123")

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_and_renders_output(self, popen_mock):
        process_mock = Mock()
        process_mock.communicate.return_value = (b"lookup output", b"")
        popen_mock.return_value = process_mock

        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn("lookup output", response.content.decode())

    @patch("introduction.other_views.subprocess.Popen")
    def test_malicious_domain_is_rejected_and_uses_generic_error(self, popen_mock):
        request = self.factory.post("/cmd_lab", {"domain": "example.com;id", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        popen_mock.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Something went wrong", response.content.decode())
