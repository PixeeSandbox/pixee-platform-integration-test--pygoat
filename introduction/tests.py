from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabValidationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.username = "cmdlabuser"
        self.password = "StrongPass123!"
        User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain(self, mocked_run):
        response = self.client.post(
            "/cmd_lab",
            {"domain": "example.com; rm -rf /", "os": "win"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mocked_run.assert_not_called()
