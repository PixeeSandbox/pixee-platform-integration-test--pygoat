from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_before_command_execution(self):
        with patch("introduction.views.subprocess.Popen") as popen:
            response = self.client.post("/cmd_lab", {"domain": "example.com; id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_without_shell(self):
        process = Mock()
        process.communicate.return_value = (b"safe output", b"")
        with patch("introduction.views.subprocess.Popen", return_value=process) as popen:
            response = self.client.post("/cmd_lab", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "safe output")
        popen.assert_called_once()
        called_args, called_kwargs = popen.call_args
        self.assertEqual(called_args[0], ["nslookup", "example.com"])
        self.assertEqual(called_kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(called_kwargs["stderr"], subprocess.PIPE)
        self.assertFalse(called_kwargs.get("shell", False))
