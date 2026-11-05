from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="cmdlab3user",
            password="StrongPassword123!",
        )
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_list_invocation_for_each_branch(self, mock_popen):
        win_process = Mock()
        win_process.communicate.return_value = (b"win output", b"")
        dig_process = Mock()
        dig_process.communicate.return_value = (b"dig output", b"")
        mock_popen.side_effect = [win_process, dig_process]

        win_response = self.client.post(
            self.url,
            {"domain": "https://www.example.com", "os": "win"},
        )
        dig_response = self.client.post(
            self.url,
            {"domain": "https://www.example.org", "os": "linux"},
        )

        self.assertEqual(win_response.status_code, 200)
        self.assertEqual(dig_response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 2)

        first_call = mock_popen.call_args_list[0]
        second_call = mock_popen.call_args_list[1]

        self.assertEqual(first_call.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", first_call.kwargs)
        self.assertEqual(second_call.args[0], ["dig", "example.org"])
        self.assertNotIn("shell", second_call.kwargs)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_process(self, mock_popen):
        response = self.client.post(
            self.url,
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertContains(response, "Invalid domain")
