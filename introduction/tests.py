from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="StrongPass123!",
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.factory = RequestFactory()

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"example output", b"")

        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs.get("shell", False))

    @patch("introduction.other_views.subprocess.Popen")
    def test_malicious_domain_is_rejected_before_popen(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            data={"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
