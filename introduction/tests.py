from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_uses_argument_list_without_shell(self):
        user = User.objects.create_user(username="tester", password="Password123!")
        self.assertTrue(self.client.login(username="tester", password="Password123!"))

        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"safe output", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=process_mock) as mock_popen:
            response = self.client.post("/cmd_lab3", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 1)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_popen(self):
        user = User.objects.create_user(username="tester2", password="Password123!")
        self.assertTrue(self.client.login(username="tester2", password="Password123!"))

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
