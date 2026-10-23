from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="cmduser",
            email="cmduser@example.com",
            password="StrongPass123!",
        )

    def test_cmd_lab_redirects_unauthenticated_users_to_login(self):
        response = self.client.get("/cmd_lab")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_benign_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process
        self.client.force_login(self.user)

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertIsInstance(called_args[0], list)
        self.assertEqual(called_args[0], ["dig", "example.com"])
        self.assertNotIn("shell", called_kwargs)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Invalid domain")
