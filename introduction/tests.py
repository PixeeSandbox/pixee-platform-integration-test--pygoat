from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="password123",
        )

    def test_cmd_lab3_uses_argv_list_for_valid_domain(self):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b"ok", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=process) as mock_popen:
            with patch("introduction.other_views.render", return_value=HttpResponse("ok")):
                response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post(
            "/cmd_lab3",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            with patch("introduction.other_views.render", return_value=HttpResponse("bad")):
                response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
