from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(self.user)

    @patch("introduction.other_views.subprocess.Popen")
    def test_valid_post_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup output", b"")

        response = self.client.post("/cmd_lab3", {"domain": "https://www.example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertIs(kwargs["shell"], False)
        self.assertContains(response, "lookup output")

    @patch("introduction.other_views.subprocess.Popen")
    def test_missing_or_malformed_domain_is_rejected(self, mock_popen):
        for data in ({"os": "win"}, {"domain": "example.com; whoami", "os": "win"}):
            with self.subTest(data=data):
                response = self.client.post("/cmd_lab3", data)
                self.assertEqual(response.status_code, 400)

        mock_popen.assert_not_called()
