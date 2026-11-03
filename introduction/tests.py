from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_hostname_uses_safe_args(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post("/cmd_lab3/", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        mock_render.assert_called_once_with(request, "Lab/CMD/cmd_lab.html", {"output": "lookup ok"})

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_injected_domain_before_process_spawn(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("invalid")

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, "Lab/CMD/cmd_lab.html", {"output": "Invalid domain"})
