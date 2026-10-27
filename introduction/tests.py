from django.test import TestCase, RequestFactory
from unittest.mock import Mock, patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = Mock(is_authenticated=True)
        mock_render.return_value = Mock()

        response = other_views.cmd_lab3(request)

        self.assertFalse(mock_popen.called)
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Invalid domain"},
        )
        self.assertEqual(response, mock_render.return_value)

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process
        mock_render.return_value = Mock()
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "https://www.example.com", "os": "linux"},
        )
        request.user = Mock(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ["dig", "example.com"])
        self.assertNotIn("shell", called_kwargs)
        self.assertEqual(called_kwargs["stdout"], other_views.subprocess.PIPE)
        self.assertEqual(called_kwargs["stderr"], other_views.subprocess.PIPE)
        mock_render.assert_called_once()
        self.assertEqual(response, mock_render.return_value)
