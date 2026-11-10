from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="cmd_lab3_user",
            password="testpass123",
        )

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com; echo injected", "os": "linux"},
        )
        request.user = self.user

        with patch("introduction.other_views.subprocess.Popen") as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, "injected")
        mock_popen.assert_not_called()
