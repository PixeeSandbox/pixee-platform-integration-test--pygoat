from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import other_views
from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_cmd_lab3_valid_domain_uses_safe_args(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen, patch(
            "introduction.other_views.render"
        ) as mock_render:
            process = mock_popen.return_value
            process.communicate.return_value = (b"example output", b"")
            mock_render.return_value = HttpResponse("rendered")

            request = self.factory.post(
                "/cmd_lab3/",
                {"domain": "https://www.example.com", "os": "win"},
            )
            request.user = self.user

            response = cmd_lab3(request)

            self.assertEqual(response.content, b"rendered")
            self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
            self.assertEqual(mock_popen.call_args.kwargs["stdout"], other_views.subprocess.PIPE)
            self.assertEqual(mock_popen.call_args.kwargs["stderr"], other_views.subprocess.PIPE)
            self.assertNotIn("shell", mock_popen.call_args.kwargs)
            mock_render.assert_called_once_with(
                request,
                "Lab/CMD/cmd_lab.html",
                {"output": "example output"},
            )

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen, patch(
            "introduction.other_views.render"
        ) as mock_render:
            mock_render.return_value = HttpResponse("rendered")

            request = self.factory.post(
                "/cmd_lab3/",
                {"domain": "bad.com;whoami", "os": "win"},
            )
            request.user = self.user

            response = cmd_lab3(request)

            self.assertEqual(response.content, b"rendered")
            mock_popen.assert_not_called()
            mock_render.assert_called_once_with(
                request,
                "Lab/CMD/cmd_lab.html",
                {"output": "Something went wrong"},
            )
