from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password123")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_executes_valid_hostname_as_argument_list(self, mock_popen, mock_render):
        request = self.factory.post("/cmd_lab3/", {"domain": "https://www.example.com", "os": "win"})
        request.user = self.user
        process = MagicMock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process
        mock_render.return_value = MagicMock()

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "lookup output"},
        )
        self.assertEqual(response, mock_render.return_value)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_popen(self, mock_popen, mock_render):
        request = self.factory.post("/cmd_lab3/", {"domain": "example.com;rm -rf /", "os": "linux"})
        request.user = self.user
        mock_render.return_value = MagicMock()

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertEqual(response, mock_render.return_value)
