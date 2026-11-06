from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_injection_payload(self):
        user = get_user_model().objects.create_user(
            username='cmduser',
            password='password123',
        )
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': 'example.com;whoami', 'os': 'win'},
            )

        self.assertContains(response, 'Invalid domain')
        mocked_popen.assert_not_called()
