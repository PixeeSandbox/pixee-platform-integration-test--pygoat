from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CommandInjectionTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user)

        with patch("introduction.views.subprocess.Popen") as popen:
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": "example.com; touch /tmp/pwned", "os": "linux"},
            )

        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()
