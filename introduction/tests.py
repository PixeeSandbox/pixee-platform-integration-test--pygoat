from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest
from django.test import RequestFactory, TestCase
from unittest.mock import patch

import introduction.views as views


class FakePopen:
    last_call = None

    def __init__(self, command, shell=False, stdout=None, stderr=None):
        type(self).last_call = {
            "command": command,
            "shell": shell,
            "stdout": stdout,
            "stderr": stderr,
        }

    def communicate(self):
        return b"lookup output\n", b""


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com; rm -rf /", "os": "win"},
        )
        request.user = self.user

        with patch.object(views.subprocess, "Popen") as mock_popen:
            response = views.cmd_lab(request)

        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_without_shell(self):
        request = self.factory.post(
            "/cmd_lab",
            data={"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        with patch.object(views.subprocess, "Popen", FakePopen):
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(FakePopen.last_call["command"], ["nslookup", "example.com"])
        self.assertFalse(FakePopen.last_call["shell"])
        self.assertEqual(FakePopen.last_call["stdout"], views.subprocess.PIPE)
        self.assertEqual(FakePopen.last_call["stderr"], views.subprocess.PIPE)
