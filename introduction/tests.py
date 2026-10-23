import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="testpass123",
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; id", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_and_preserves_lookup_command(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        for os_value, expected_command in (("win", "nslookup"), ("linux", "dig")):
            request = self.factory.post(
                "/cmd_lab3",
                {"domain": "example.com", "os": os_value},
            )
            request.user = self.user

            response = cmd_lab3(request)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "lookup ok")
            mock_popen.assert_called_with(
                [expected_command, "example.com"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )

        self.assertEqual(mock_popen.call_count, 2)
