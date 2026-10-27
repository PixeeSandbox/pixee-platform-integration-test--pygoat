from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

import introduction.views as views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="cmdlabuser", password="password123")

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_safe_domain(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"example output", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
