from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_safe_argument_list_for_valid_domain(self, mock_popen, mock_render):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"answer", b"")

        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "https://www.example.com", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "answer"},
        )

    @patch("introduction.views.render", return_value=HttpResponse("ok"))
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_popen(self, mock_popen, mock_render):
        request = self.factory.post(
            "/cmd_lab/",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Invalid domain"},
        )
