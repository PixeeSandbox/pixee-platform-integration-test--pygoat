from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch

from introduction import views


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="testpassword123",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ["nslookup", "example.com"],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertContains(response, "ok")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_calling_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")
