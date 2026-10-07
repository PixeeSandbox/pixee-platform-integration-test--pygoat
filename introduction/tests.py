import subprocess
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch


class CmdLabCommandInjectionTests(TestCase):
    def test_cmd_lab_uses_argument_list_for_domain(self):
        user = get_user_model().objects.create_user(
            username="cmduser",
            password="StrongPass123!",
        )
        self.client.force_login(user)
        mocked_process = Mock()
        mocked_process.communicate.return_value = (b"", b"")

        with patch("introduction.views.subprocess.Popen", return_value=mocked_process) as popen_mock:
            response = self.client.post(
                reverse("Command Injection Lab"),
                {"domain": "example.com; id", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ["dig", "example.com; id"])
        self.assertNotIn("shell", kwargs)
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
