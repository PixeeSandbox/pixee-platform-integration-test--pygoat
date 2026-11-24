from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="cmdtest", password="test-password")
        self.client.force_login(user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malformed_domain(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b"lookup result", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ["dig", "example.com"])
        self.assertFalse(mock_popen.call_args.kwargs["shell"])
