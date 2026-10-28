from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="cmdpass123")
        self.url = reverse("Command Injection Lab")

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        self.client.force_login(self.user)
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b"valid output", b"")

            response = self.client.post(
                self.url,
                {"domain": "example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "valid output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)

    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self):
        self.client.force_login(self.user)
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                self.url,
                {"domain": "example.com; whoami", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["output"], "Something went wrong")
        mock_popen.assert_not_called()
