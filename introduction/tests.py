from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="testpassword123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; whoami", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertEqual(response.context["output"], "Invalid domain")

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        process = patch("introduction.views.subprocess.Popen")
        with process as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"resolved\n", b"")

            response = self.client.post(
                "/cmd_lab",
                {"domain": "https://www.Example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", mock_popen.call_args.kwargs)
        self.assertEqual(response.context["output"], "resolved\n")
