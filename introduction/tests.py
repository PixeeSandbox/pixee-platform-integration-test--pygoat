from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3SecurityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="securitytester", password="StrongPassword123!")
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        malicious_domain = "example.com; touch /tmp/pwned"

        with patch("introduction.other_views.subprocess.Popen") as mocked_popen:
            response = self.client.post("/cmd_lab3", {"domain": malicious_domain, "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mocked_popen.assert_not_called()
