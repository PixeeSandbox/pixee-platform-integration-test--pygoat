from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_run, mock_render):
        mock_render.return_value = Mock()
        request = self.factory.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "linux"})
        request.user = Mock(is_authenticated=True)

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertIs(response, mock_render.return_value)
        self.assertEqual(mock_render.call_args[0][2]["output"], "Invalid domain")

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.run")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run, mock_render):
        mock_run.return_value = Mock(stdout="ok", stderr="")
        mock_render.return_value = Mock()
        request = self.factory.post("/cmd_lab3", {"domain": "example.com", "os": "win"})
        request.user = Mock(is_authenticated=True)

        response = cmd_lab3(request)

        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[0][0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_run.call_args.kwargs)
        self.assertTrue(mock_run.call_args.kwargs["capture_output"])
        self.assertTrue(mock_run.call_args.kwargs["text"])
        self.assertFalse(mock_run.call_args.kwargs["check"])
        self.assertIs(response, mock_render.return_value)
