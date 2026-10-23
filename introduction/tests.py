from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="cmdlab3user",
            password="Password123!",
        )
        self.assertTrue(
            self.client.login(username="cmdlab3user", password="Password123!")
        )

    def test_malicious_domain_is_rejected_without_subprocess(self):
        with patch("introduction.other_views.subprocess.Popen") as mocked_popen:
            response = self.client.post(
                "/cmd_lab3",
                {
                    "domain": "https://www.example.com;id",
                    "os": "win",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Something went wrong", response.content)
        mocked_popen.assert_not_called()

    def test_valid_hostname_uses_argument_list_without_shell(self):
        with patch("introduction.other_views.subprocess.Popen") as mocked_popen:
            mocked_process = mocked_popen.return_value
            mocked_process.communicate.return_value = (b"lookup output", b"")
            response = self.client.post(
                "/cmd_lab3",
                {
                    "domain": "example.com",
                    "os": "win",
                },
            )

        self.assertEqual(response.status_code, 200)
        mocked_popen.assert_called_once()
        args, kwargs = mocked_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", True))
