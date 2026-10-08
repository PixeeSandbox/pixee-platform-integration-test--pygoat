from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdtester",
            password="password123",
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_and_disables_shell(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b"lookup ok", b"")
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
        self.assertEqual(mock_popen.call_args.kwargs["stdout"], -1)
        self.assertEqual(mock_popen.call_args.kwargs["stderr"], -1)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malformed_domain_before_popen(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
