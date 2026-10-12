from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdtester",
            password="strong-password-123",
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain(self):
        malicious_domain = "example.com;whoami"

        with mock.patch("introduction.other_views.subprocess.run") as run_mock:
            response = self.client.post(
                "/cmd_lab3",
                {
                    "domain": malicious_domain,
                    "os": "win",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        self.assertNotContains(response, malicious_domain)
        run_mock.assert_not_called()
