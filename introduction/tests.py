from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="tester", password="pass12345")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.Popen")
    def test_malicious_domain_is_rejected_without_invoking_popen(self, mock_popen):
        response = self.client.post(
            self.url,
            {"domain": "example.com; whoami", "os": "linux"},
        )

        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_benign_lookup_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"answer\n", b"")

        response = self.client.post(
            self.url,
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "answer")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
