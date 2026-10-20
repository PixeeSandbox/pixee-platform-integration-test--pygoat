from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlab-user",
            password="password123",
        )

    def _build_request(self, domain, os_choice):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": domain, "os": os_choice},
        )
        request.user = self.user
        return request

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_valid_post_uses_argument_list(self, mock_run):
        mock_run.return_value = MagicMock(stdout="lookup ok\n", stderr="")
        request = self._build_request("https://www.example.com", "win")

        response = cmd_lab3(request)

        self.assertIsInstance(response, HttpResponse)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertIn(b"lookup ok", response.content)

    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_injected_domain_before_subprocess(self, mock_run):
        request = self._build_request("example.com; rm -rf /", "linux")

        response = cmd_lab3(request)

        self.assertIsInstance(response, HttpResponse)
        mock_run.assert_not_called()
        self.assertIn(b"Something went wrong", response.content)
