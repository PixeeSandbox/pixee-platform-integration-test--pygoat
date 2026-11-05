from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "bad.com;id", "os": "win"}
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(
            mock_render.call_args.kwargs["output"],
            "Something went wrong"
        )

    @patch("introduction.other_views.render")
    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argv_list_without_shell(self, mock_popen, mock_render):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"OK", b"")
        mock_render.return_value = HttpResponse("rendered")
        request = self.factory.post(
            "/cmd_lab3/",
            data={"domain": "example.com", "os": "win"}
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b"rendered")
        mock_popen.assert_called_once()
        popen_args, popen_kwargs = mock_popen.call_args
        self.assertEqual(popen_args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", popen_kwargs)
        self.assertEqual(popen_kwargs["stdout"], other_views.subprocess.PIPE)
        self.assertEqual(popen_kwargs["stderr"], other_views.subprocess.PIPE)
        self.assertEqual(
            mock_render.call_args.kwargs["output"],
            "OK"
        )
