from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="pass12345",
        )

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_domain_uses_safe_subprocess_arguments(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injected_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("bad request")

        request = self.factory.post("/cmd_lab", {"domain": "example.com;id", "os": "win"})
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Something went wrong"},
        )
        self.assertEqual(response.status_code, 200)
