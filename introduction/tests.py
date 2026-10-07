import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password123")

    def test_cmd_lab_rejects_malicious_domain_without_shell_execution(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Something went wrong", response.content)
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_and_shell_false_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as process_mock:
            process_mock.return_value.communicate.return_value = (b"resolved", b"")

            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"resolved", response.content)
        process_mock.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
