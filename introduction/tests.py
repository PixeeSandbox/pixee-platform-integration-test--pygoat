from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class TestCmdLab3(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlab3-user",
            password="password123",
        )

    def _build_request(self, domain, os_value):
        request = self.factory.post("/cmd_lab", {"domain": domain, "os": os_value})
        request.user = self.user
        return request

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_injected_domain_before_subprocess(self, mock_popen):
        request = self._build_request("example.com; rm -rf /", "linux")
        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        request = self._build_request("example.com", "win")
        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup output")
