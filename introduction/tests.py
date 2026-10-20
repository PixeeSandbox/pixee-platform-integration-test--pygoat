from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="tester-pass")
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post("/cmd_lab", {"domain": "example.com; rm -rf /", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        mock_popen.assert_not_called()

    def test_cmd_lab_accepts_safe_domain(self):
        process = Mock()
        process.communicate.return_value = (b"lookup ok", b"")

        with patch("introduction.views.subprocess.Popen", return_value=process) as mock_popen:
            response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lookup ok")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertNotIn("shell", kwargs)
