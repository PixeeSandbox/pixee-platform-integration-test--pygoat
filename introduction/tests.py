from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="StrongPass123!")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_uses_argument_list_for_safe_domains(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"SAFE OUTPUT", b"")

        for os_name, expected_command in (("linux", ["dig", "example.com"]), ("win", ["nslookup", "example.com"])):
            with self.subTest(os_name=os_name):
                response = self.client.post(self.url, {"domain": "example.com", "os": os_name})

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "SAFE OUTPUT")
                self.assertEqual(mock_popen.call_args[0][0], expected_command)
                self.assertNotIn("shell", mock_popen.call_args.kwargs)
                mock_popen.reset_mock()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_injected_domain(self, mock_popen):
        response = self.client.post(self.url, {"domain": "example.com;whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
