import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )
        self.client = Client()
        self.client.force_login(self.user)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(mock_render.call_args.args[2], {"output": "Something went wrong"})

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argv_and_shell_false(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse("rendered")
        mock_run.return_value = type("Result", (), {"stdout": "lookup ok", "stderr": ""})()

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], "Lab/CMD/cmd_lab.html")
        self.assertEqual(mock_render.call_args.args[2], {"output": "lookup ok"})
