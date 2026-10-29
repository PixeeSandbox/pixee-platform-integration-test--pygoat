from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

    def _build_request(self, domain, os_value="linux"):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": domain, "os": os_value},
        )
        request.user = self.user
        return request

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("invalid")

        response = cmd_lab(self._build_request("example.com; rm -rf /"))

        self.assertEqual(response.content, b"invalid")
        mock_popen.assert_not_called()
        self.assertEqual(mock_render.call_args[0][2]["output"], "Something went wrong")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b"example response", b"")
        mock_render.return_value = HttpResponse("valid")

        response = cmd_lab(self._build_request("https://www.example.com", "win"))

        self.assertEqual(response.content, b"valid")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(mock_render.call_args[0][2]["output"], "example response")
