from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="TestPass123!",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters_without_invoking_subprocess(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com; rm -rf /", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": "example.com", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
