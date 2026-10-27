from unittest.mock import ANY, Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def test_command_injection_domain_is_passed_as_literal_argument(self):
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(user)

        malicious_domain = "example.com; echo pwned"

        process = Mock()
        process.communicate.return_value = (b"safe output", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": malicious_domain, "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "safe output")
        self.assertNotContains(response, "pwned")
        mock_popen.assert_called_once_with(
            ["dig", malicious_domain],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
