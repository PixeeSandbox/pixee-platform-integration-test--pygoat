from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="testuser", password="password")

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain_input(self, mock_popen):
        request = self.factory.post("/cmd_lab", {"domain": "example.com; id", "os": "linux"})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()
