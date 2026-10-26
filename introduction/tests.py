from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mocked_popen:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'google.com && whoami', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid input')
        mocked_popen.assert_not_called()
