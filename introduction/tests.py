from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from . import other_views


class FakeUser:
    is_authenticated = True


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_valid_hostname_uses_argument_list(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b"stdout", b"stderr")
        mock_popen.return_value = process
        mock_render.return_value = MagicMock()

        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = FakeUser()

        other_views.cmd_lab3(request)

        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ["nslookup", "example.com"])
        self.assertFalse(called_kwargs["shell"])
        self.assertNotIsInstance(called_args[0], str)
        mock_render.assert_called_once()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = MagicMock()

        request = self.factory.post("/cmd_lab3", {"domain": "example.com;rm -rf /", "os": "win"})
        request.user = FakeUser()

        other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]["output"], "Something went wrong")
