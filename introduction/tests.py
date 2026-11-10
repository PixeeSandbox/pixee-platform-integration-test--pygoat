from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.password = "securepass123"
        cls.user = cls.User.objects.create_user(username="cmduser", password=cls.password)

    def setUp(self):
        self.assertTrue(self.client.login(username="cmduser", password=self.password))

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": "example.com;id", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, "Something went wrong")

    def test_cmd_lab_uses_argument_list_without_shell(self):
        with patch("introduction.views.subprocess.Popen") as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b"lookup ok", b"")
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": "example.com", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ["nslookup", "example.com"])
        self.assertFalse(called_kwargs["shell"])
        self.assertContains(response, "lookup ok")
