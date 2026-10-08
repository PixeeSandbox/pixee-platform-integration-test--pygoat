import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com;whoami", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        process = patch("introduction.other_views.subprocess.Popen")
        with process as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"nslookup ok\n", b"")
            response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nslookup ok")
