from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            password="password123",
        )

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post(
            "/cmd_lab/",
            {
                "domain": "example.com;whoami",
                "os": "win",
            },
        )
        request.user = self.user

        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid domain", response.content.decode())
        mock_popen.assert_not_called()
