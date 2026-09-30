from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


User = get_user_model()


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="cmdlab3user", password="password123")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"lookup output", b"")
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])

        request = self.factory.post("/cmd_lab3/", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(response.content.decode(), "lookup output")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_malicious_domain_is_rejected_before_execution(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])

        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content.decode(), "Something went wrong")
