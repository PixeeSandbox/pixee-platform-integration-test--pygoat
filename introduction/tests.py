from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CommandInjectionLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(self.user)

    def test_invalid_domain_rejected_without_running_subprocess(self):
        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab3", {"domain": "example.com; rm -rf /", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()

    def test_valid_domain_uses_argv_list_and_disables_shell(self):
        process = patch("introduction.other_views.subprocess.Popen")
        with process as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"lookup output", b"")
            response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertFalse(kwargs["shell"])

