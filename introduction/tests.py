import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="password123")

    def _make_request(self, domain, os_value):
        request = self.factory.post("/cmd_lab3/", data={"domain": domain, "os": os_value})
        request.user = self.user
        return request

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self._make_request("example.com; whoami", "win")
        with patch("introduction.other_views.subprocess.Popen") as mock_popen, patch(
            "introduction.other_views.render",
            return_value=HttpResponse("Something went wrong"),
        ) as mock_render:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request, "Lab/CMD/cmd_lab.html", {"output": "Something went wrong"}
        )
        self.assertEqual(response.content, b"Something went wrong")

    def test_cmd_lab3_uses_argument_list_with_shell_disabled_for_valid_domain(self):
        request = self._make_request("example.com", "win")
        process = MagicMock()
        process.communicate.return_value = (b"resolved", b"")
        with patch("introduction.other_views.subprocess.Popen", return_value=process) as mock_popen, patch(
            "introduction.other_views.render",
            return_value=HttpResponse("resolved"),
        ) as mock_render:
            response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()
        self.assertEqual(response.content, b"resolved")
