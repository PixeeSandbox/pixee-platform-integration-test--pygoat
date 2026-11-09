import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="cmduser", password="safepassword123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_safe_argv_for_valid_domain(self, mock_run):
        mock_run.return_value.stdout = "resolved\n"
        mock_run.return_value.stderr = "extra\n"

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertTrue(kwargs["text"])
        self.assertEqual(response.context["output"], "resolved\nextra\n")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post("/cmd_lab", {"domain": "example.com;rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertEqual(response.context["output"], "Invalid domain")
