from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_domain_uses_argument_vector_without_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"valid output", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertEqual(response.context["output"], "valid output")

    @patch("introduction.other_views.subprocess.Popen")
    def test_malicious_domain_is_rejected_without_executing_command(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertEqual(response.context["output"], "Invalid domain provided")
