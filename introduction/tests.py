from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_vector_for_valid_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        process = mock_popen.return_value
        process.communicate.return_value = (b"answer", b"")

        request = self.factory.post("/cmd_lab/", data={"domain": "example.com", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.content, b"rendered")
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

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injected_domain_before_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse("rendered")

        request = self.factory.post("/cmd_lab/", data={"domain": "example.com;id", "os": "win"})
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.content, b"rendered")
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            "Lab/CMD/cmd_lab.html",
            {"output": "Invalid domain"},
        )
