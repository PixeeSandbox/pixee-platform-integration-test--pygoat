from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="strong-password123",
        )
        self.assertTrue(self.client.login(username="cmdlabuser", password="strong-password123"))

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_vector_for_valid_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b"lookup ok", b"")

        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ["nslookup", "example.com"])
        self.assertFalse(called_kwargs["shell"])
        self.assertEqual(response.context[-1]["output"], "lookup ok")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_hostname_before_subprocess(self, mock_popen):
        response = self.client.post(
            "/cmd_lab3",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(response.context[-1]["output"], "Something went wrong")
