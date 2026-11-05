from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="cmdtester", password="pass12345")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_posts_safe_domain_with_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"example output", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "example output")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_before_spawning_process(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "win"})

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Invalid domain")
