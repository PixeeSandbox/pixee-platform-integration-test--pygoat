from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password123",
        )

    @patch("introduction.other_views.render", return_value="rendered response")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b"ok", b"")

        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response, "rendered response")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))

    @patch("introduction.other_views.render", return_value="rendered response")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_spawn(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com;rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response, "rendered response")
        mock_popen.assert_not_called()
