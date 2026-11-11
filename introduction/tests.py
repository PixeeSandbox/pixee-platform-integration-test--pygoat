from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CommandInjectionTests(TestCase):
    def test_reject_invalid_domain_without_launching_process(self):
        user = get_user_model().objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.Popen") as process_launcher:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; touch /tmp/injected", "os": "win"},
            )

        self.assertEqual(response.status_code, 400)
        process_launcher.assert_not_called()
