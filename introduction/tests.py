from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )

    def test_cmd_lab_rejects_malicious_domain_without_spawning_process(self):
        self.client.force_login(self.user)

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; id", "os": "linux"},
            )

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")

    def test_cmd_lab_uses_argv_list_with_shell_false_for_valid_domain(self):
        self.client.force_login(self.user)
        process = MagicMock()
        process.communicate.return_value = (b"resolved", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
