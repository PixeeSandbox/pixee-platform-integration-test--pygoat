from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="secret123")
        self.client.login(username="cmduser", password="secret123")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; cat /etc/passwd", "os": "linux"})

        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_accepts_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"resolver output", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolver output")
        mock_popen.assert_called_once()
