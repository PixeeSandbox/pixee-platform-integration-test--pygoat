from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_passes_domain_as_single_argument(self, mock_popen, mock_render):
        malicious_domain = "example.com; whoami"
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": malicious_domain, "os": "linux"},
        )
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b"stdout", b"stderr")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        response = cmd_lab3(request)

        self.assertEqual(response.content, b"ok")
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", malicious_domain])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
