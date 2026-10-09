from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': 'example.com; echo injected', 'os': 'linux'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
