from django.test import TestCase, RequestFactory
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock(is_authenticated=True)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_invalid_domain_without_popen(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "example.com;rm -rf /", "os": "win"},
        )
        request.user = self.user
        mock_render.return_value = Mock()

        response = cmd_lab3(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"good", b"")
        mock_popen.return_value = process
        mock_render.return_value = Mock()

        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertFalse(kwargs.get("shell", False))
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "good"},
        )
