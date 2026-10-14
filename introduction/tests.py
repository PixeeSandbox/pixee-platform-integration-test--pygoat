from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="tester", password="password")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup ok", b"")
        request = self.factory.post("/cmd_lab", {"domain": "https://www.example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=mock_popen.call_args.kwargs["stdout"],
            stderr=mock_popen.call_args.kwargs["stderr"],
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_executing_command(self, mock_popen):
        request = self.factory.post("/cmd_lab", {"domain": "example.com; whoami", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
