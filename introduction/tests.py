from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmduser",
            email="cmduser@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    def _post_cmd_lab(self, os_value):
        process = Mock()
        process.communicate.return_value = (b"lookup output", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as popen:
            response = self.client.post(
                "/cmd_lab",
                {
                    "domain": "https://www.example.com; touch /tmp/pwned",
                    "os": os_value,
                },
            )

        return response, popen

    def test_cmd_lab_uses_nslookup_for_windows(self):
        response, popen = self._post_cmd_lab("win")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(popen.call_count, 1)
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com; touch /tmp/pwned"])
        self.assertFalse(kwargs.get("shell", False))

    def test_cmd_lab_uses_dig_by_default(self):
        response, popen = self._post_cmd_lab("")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(popen.call_count, 1)
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ["dig", "example.com; touch /tmp/pwned"])
        self.assertFalse(kwargs.get("shell", False))
