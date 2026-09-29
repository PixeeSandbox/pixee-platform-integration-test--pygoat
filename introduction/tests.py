from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {
                "domain": "example.com;id",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_vector_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        response = self.client.post(
            reverse("Command Injection Lab 3"),
            {
                "domain": "example.com",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "lookup ok")
        mock_popen.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            stdout=-1,
            stderr=-1,
        )
