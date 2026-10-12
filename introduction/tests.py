from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import Mock, patch


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com; touch /tmp/pwned",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid input")
        self.assertNotIn(b"pwned", response.content)
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_accepts_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")
        mock_popen.return_value = process

        response = self.client.post(
            "/cmd_lab",
            {
                "domain": "example.com",
                "os": "linux",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
