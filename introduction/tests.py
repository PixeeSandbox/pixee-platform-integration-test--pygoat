from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="Password123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_accepts_valid_domain_and_uses_safe_argument_list(self, mock_run):
        mock_run.return_value = Mock(stdout="lookup ok", stderr="")

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_run.assert_called_once_with(
            ["dig", "example.com"],
            shell=False,
            capture_output=True,
            text=True,
        )

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_execution(self, mock_run):
        for payload in ("example.com; whoami", "example.com && dir"):
            with self.subTest(payload=payload):
                response = self.client.post(
                    "/cmd_lab",
                    {"domain": payload, "os": "linux"},
                )

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Something went wrong")
                self.assertNotContains(response, payload)
                mock_run.assert_not_called()
                mock_run.reset_mock()
