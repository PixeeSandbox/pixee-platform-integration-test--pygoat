from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="testpassword123",
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("safe")
        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "example.com; whoami", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"safe")
        self.assertEqual(mock_render.call_args[0][2]["output"], "Invalid input")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("safe")
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"resolved\n", b"")
        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"safe")
