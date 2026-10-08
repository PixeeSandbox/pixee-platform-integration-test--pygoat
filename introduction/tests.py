from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cmdlabuser",
            password="StrongPassword123!",
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_input(self):
        malicious_domain = "example.com;whoami"

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                "/cmd_lab",
                {"domain": malicious_domain, "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, malicious_domain)
        mock_popen.assert_not_called()
