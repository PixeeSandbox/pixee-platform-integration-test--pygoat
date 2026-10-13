from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="cmdlab3user", password="StrongPass123!")
        self.client.force_login(self.user)
        self.url = reverse("Command Injection Lab 3")

    def _post_malicious_domain(self, os_value):
        malicious_domain = "example.com; touch /tmp/pwned"
        with patch("introduction.other_views.subprocess.Popen") as popen_mock:
            response = self.client.post(self.url, {"domain": malicious_domain, "os": os_value})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "pwned")
        popen_mock.assert_not_called()

    def test_cmd_lab3_rejects_malicious_domain_on_windows_branch(self):
        self._post_malicious_domain("win")

    def test_cmd_lab3_rejects_malicious_domain_on_non_windows_branch(self):
        self._post_malicious_domain("linux")
