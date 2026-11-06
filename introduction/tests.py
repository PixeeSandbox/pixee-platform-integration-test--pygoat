from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_injected_domain(self):
        user = get_user_model().objects.create_user(username="tester", password="password")
        request = RequestFactory().post(
            "/cmd_lab3",
            data={"domain": "example.com; id", "os": "linux"},
        )
        request.user = user

        with patch("introduction.other_views.subprocess.Popen") as popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        popen.assert_not_called()
