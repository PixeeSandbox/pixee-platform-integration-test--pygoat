from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="StrongPassword123!")

    def test_cmd_lab_rejects_malicious_domain_and_uses_argv(self):
        self.client.login(username="cmduser", password="StrongPassword123!")

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab", {"domain": "example.com;id", "os": "linux"})
            self.assertContains(response, "Something went wrong")
            mock_popen.assert_not_called()

            process = Mock()
            process.communicate.return_value = (b"safe output", b"")
            mock_popen.reset_mock()
            mock_popen.return_value = process

            response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})
            self.assertContains(response, "safe output")
            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            self.assertEqual(args[0], ["dig", "example.com"])
            self.assertFalse(kwargs.get("shell", False))
