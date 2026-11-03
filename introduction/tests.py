from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import ANY, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argv_list_and_disables_shell(self, mock_popen):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"valid output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com;rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
