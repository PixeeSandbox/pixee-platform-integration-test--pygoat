from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cmd_user", password="StrongPass123!")
        self.client.login(username="cmd_user", password="StrongPass123!")

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_linux(self, mock_popen):
        payload = "example.com;id"
        response = self.client.post("/cmd_lab", {"domain": payload, "os": "linux"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, payload)
        mock_popen.assert_not_called()

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_windows(self, mock_popen):
        payload = "example.com && whoami"
        response = self.client.post("/cmd_lab", {"domain": payload, "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, payload)
        mock_popen.assert_not_called()
