from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cmduser", password="pass12345")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post("/cmd_lab", {"domain": "example.com; whoami", "os": "linux"})

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
