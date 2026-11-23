from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdtest", password="password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "win"})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_runs_valid_domain_as_argument(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once()
        self.assertEqual(popen.call_args[0][0], ["nslookup", "example.com"])
        self.assertIs(popen.call_args[1]["shell"], False)
