from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_cmd_lab3_valid_domain_uses_argument_list(self):
        self.assertTrue(self.client.login(username="testuser", password="testpass123"))
        process_mock = Mock()
        process_mock.communicate.return_value = (b"resolved", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=process_mock) as mock_popen:
            response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resolved")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)

    def test_cmd_lab3_rejects_malicious_domain(self):
        self.assertTrue(self.client.login(username="testuser", password="testpass123"))

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab3", {"domain": "example.com; id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
