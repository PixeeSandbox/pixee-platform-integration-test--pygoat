from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="password123",
        )

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "example.com && id", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen, \
             patch("introduction.other_views.render", return_value=MagicMock()) as mock_render:
            cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertTrue(mock_render.called)
        self.assertEqual(mock_render.call_args[0][2]["output"], "Invalid domain")

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post(
            "/cmd_lab3/",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"lookup output", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=process_mock) as mock_popen, \
             patch("introduction.other_views.render", return_value=MagicMock()):
            cmd_lab3(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs.get("shell", True))
