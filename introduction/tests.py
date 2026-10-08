from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        User = get_user_model()
        self.user = User.objects.create_user(username="cmduser", password=self.password)

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        self.client.login(username="cmduser", password=self.password)
        process = MagicMock()
        process.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.other_views.subprocess.Popen", return_value=process) as mock_popen:
            response = self.client.post("/cmd_lab3", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell"))
        self.assertContains(response, "lookup ok")

    def test_cmd_lab3_rejects_malicious_domain_without_running_subprocess(self):
        self.client.login(username="cmduser", password=self.password)

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab3", {"domain": "example.com;whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")
