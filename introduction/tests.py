import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_cmd_lab_rejects_injection_payload(self):
        request = self.factory.post("/cmd_lab", {"domain": "example.com;id", "os": "win"})
        request.user = self.user

        with patch("introduction.views.subprocess.run") as mock_run:
            response = cmd_lab(request)

        self.assertIn("Invalid domain", response.content.decode())
        mock_run.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_hostname(self):
        request = self.factory.post("/cmd_lab", {"domain": "example.com", "os": "win"})
        request.user = self.user

        mock_process = type("MockProcess", (), {"stdout": "lookup output", "stderr": ""})()
        with patch("introduction.views.subprocess.run", return_value=mock_process) as mock_run:
            response = cmd_lab(request)

        self.assertIn("lookup output", response.content.decode())
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
