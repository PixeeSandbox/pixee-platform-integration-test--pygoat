import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_running_command(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; id", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"example output", b"")
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "https://www.Example.com.", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertContains(response, "example output")
