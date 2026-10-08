from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_returns_output_for_safe_domain(self, mock_popen):
        self.assertTrue(self.client.login(username="cmduser", password="StrongPass123!"))

        mock_popen.return_value.communicate.return_value = (b"safe output", b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "safe output")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        self.assertTrue(self.client.login(username="cmduser", password="StrongPass123!"))

        response = self.client.post("/cmd_lab", {"domain": "example.com;id", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
