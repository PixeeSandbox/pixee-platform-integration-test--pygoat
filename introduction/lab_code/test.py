from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="password123")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_valid_hostname_uses_argv_list_without_shell(self, mock_run):
        mock_run.return_value = MagicMock(stdout="valid output", stderr="")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid output")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_run.assert_not_called()
