from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

import introduction.views as views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_safe_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"safe output", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab",
            {"domain": " https://www.example.com ", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], views.subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], views.subprocess.PIPE)
        self.assertContains(response, "safe output")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_input(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab",
            {"domain": "example.com; cat /etc/passwd", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
