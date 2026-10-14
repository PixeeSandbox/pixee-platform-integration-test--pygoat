from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabCommandInjectionRegressionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="StrongPass123!")
        self.client.login(username="cmduser", password="StrongPass123!")

    @patch("introduction.views.subprocess.run")
    def test_rejects_malicious_domain_input(self, mock_run):
        response = self.client.post(
            reverse("Command Injection Lab"),
            {"domain": "example.com;id", "os": "linux"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, "example.com;id")
        mock_run.assert_not_called()
