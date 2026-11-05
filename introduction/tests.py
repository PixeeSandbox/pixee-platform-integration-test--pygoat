from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_list_invocation_for_valid_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"resolved example.com", b"")
        mock_popen.return_value = process

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "  https://www.example.com  ", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["stdout"], views.subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], views.subprocess.PIPE)
        self.assertContains(response, "resolved example.com")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com; cat /etc/passwd", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")
