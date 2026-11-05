from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    @patch("introduction.other_views.subprocess.Popen")
    def test_authenticated_post_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"ok", b"")

        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)

    @patch("introduction.other_views.subprocess.Popen")
    def test_authenticated_post_rejects_malicious_domain_without_popen(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_unauthenticated_request_redirects_to_login(self):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = AnonymousUser()

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)
